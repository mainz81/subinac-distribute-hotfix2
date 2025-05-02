import { Keypair, Server, TransactionBuilder, Networks, Operation, Asset } from 'stellar-sdk';

const server = new Server('https://horizon.stellar.org');

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method Not Allowed' });
  }

  const { secret } = req.body;

  if (secret !== process.env.SUBINAC_SECRET) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  try {
    const sourceKeypair = Keypair.fromSecret(process.env.PRIVATE_KEY);
    const sourcePublicKey = sourceKeypair.publicKey();
    const account = await server.loadAccount(sourcePublicKey);
    const fee = await server.fetchBaseFee();

    const totalBalance = account.balances.find(b => b.asset_type === 'native').balance;
    const available = parseFloat(totalBalance) - 1; // buffer

    const distribution = {
      "GA6HJZK5XU73QH46VC2Y5SFWXTRFBQOAS44QH42LU3UU2HV": 0.2125, // Michael
      "GA2WZSDGZZETJQ4GSM4OHFKTYC7ZIS5JE227QMBNH3YL24DU2MGQ2WR5": 0.2125, // Canibus
      "GA2ZTYJZVFLQ7XY3T7QRXGSGNEG46DG3TKSYL7JKGXOTJEVBHNFIPJWS": 0.2125, // Shan
      "GAZEKR2TL5LSJ2R2DGEPCF4OUBKPGGPVIOD2BLHXMQXXMURN6JBQO6SQ": 0.2125, // Phaze
      "GAERT6JAYBF2RKO2SV4BOPH7NOTBV533UWNSXRTBJPJEXC4ZATULZIZX": 0.15  // Core Phore Tech
    };

    const txBuilder = new TransactionBuilder(account, {
      fee,
      networkPassphrase: Networks.PUBLIC
    });

    for (const [wallet, percent] of Object.entries(distribution)) {
      const amount = (available * percent).toFixed(7);
      txBuilder.addOperation(Operation.payment({
        destination: wallet,
        asset: Asset.native(),
        amount
      }));
    }

    const transaction = txBuilder.setTimeout(30).build();
    transaction.sign(sourceKeypair);

    const result = await server.submitTransaction(transaction);

    res.status(200).json({
      success: true,
      hash: result.hash
    });
  } catch (err) {
    console.error('Distribution error:', err);
    res.status(500).json({
      success: false,
      message: err.message
    });
  }
}
