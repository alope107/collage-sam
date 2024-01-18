### Steps for deployment

Assumes you already have:
- A public S3 bucket with an index.html that holds the site
- A domain hosted on Route 53.

TODO(auberon): Have the bucket be managed by this template as well.

1. `sam build --use-container`
1. `sam deploy --guided`
1. Make sure to set the root domain name when prompted. NO LEADING www!
1. The first time this is deployed, the deployment will wait on the validation of the certificate. You will need to validate the certificate manually in the AWS console.
   - As the deployment is waiting, open the Certificate Manager in the AWS Console
   - You should see a certificate that is pending validation.
   - On this certificate's page there will be two pairs of CNAME names and values.
   - In a separate tab, go to the Route 53 page for your hosted zone (domain).
   - Add a new record set (Add record, then in the same page add a second record before submitting).
   - For the name and values, copy the entries from the certificate manager page.
   - For type, choose CNAME.
   - Once you submit the new records, it may take a few minutes for the validation to complete. You can check this status in the Certificate Manager page
   - Shortly after validation the sam deployment that was pending on the command line should complete.
   - Fingers crossed, this only needs to happen the first time you deploy!
