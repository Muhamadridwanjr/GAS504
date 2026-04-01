const {GoogleAuth} = require('google-auth-library');
async function main() {
  const auth = new GoogleAuth({
    scopes: 'https://www.googleapis.com/auth/cloud-platform'
  });
  const client = await auth.getClient();
  const project = await auth.getProjectId();
  console.log(`Berhasil! Project ID: ${project}`);
}
main();
