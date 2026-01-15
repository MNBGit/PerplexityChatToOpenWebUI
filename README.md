<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# in cloudflare by is it that my domain domain.tld doesn't work but www.domaine.tld do ?

When your root domain (domain.tld) works but www.domain.tld doesn't in Cloudflare, this is typically caused by missing or incorrect DNS records. You need to have **two separate DNS records** configured in Cloudflare for both versions to work properly.[^1_1][^1_3]

## Missing DNS Record Configuration

The most common cause is having a DNS record for `www` but not for your root domain `@`. In Cloudflare's DNS settings, you need:[^1_3]

- An A record (or CNAME) with **Name** set to `@` pointing to your server/service
- A separate A record (or CNAME) with **Name** set to `www` pointing to the same destination[^1_3]


## How to Fix It

Navigate to your Cloudflare DNS settings and verify you have both records:

- **Root domain record**: Type: A or CNAME, Name: `@`, Target: your server IP or destination
- **WWW subdomain record**: Type: A or CNAME, Name: `www`, Target: same server IP or destination[^1_3]

Set **Proxy status** to "DNS only" initially to ensure proper DNS resolution, especially if you're setting up SSL certificates. After DNS propagates (usually a few minutes), both versions should work. You can then optionally enable Cloudflare's proxy after confirming both domains resolve correctly.[^1_3]

If you want one version to redirect to the other (e.g., force www or remove www), you can set up a redirect rule in Cloudflare's dashboard after both DNS records are functioning.[^1_5]
<span style="display:none">[^1_10][^1_11][^1_12][^1_2][^1_4][^1_6][^1_7][^1_8][^1_9]</span>

<div align="center">â‚</div>

[^1_1]: https://stackoverflow.com/questions/32622722/domain-without-www-on-cloudflare

[^1_2]: https://www.reddit.com/r/developersIndia/comments/1h7w5cm/how_is_cloudflare_domains_and_hosting_compared_to/

[^1_3]: https://render.com/docs/configure-cloudflare-dns

[^1_4]: https://www.reddit.com/r/nginxproxymanager/comments/1gnnutn/proxy_not_working_with_a_homemydomaintld/

[^1_5]: https://www.reddit.com/r/CloudFlare/comments/1dizwmr/cloudflare_page_issue_accessing_custom_domain/

[^1_6]: https://developers.cloudflare.com/fundamentals/manage-domains/add-site/

[^1_7]: https://forum.openwrt.org/t/solved-cloudflare-dyndns/56896

[^1_8]: https://www.facebook.com/groups/cyberpanel/posts/2177788952532741/

[^1_9]: https://forum.virtualmin.com/t/web-hosting-problem-and-ips/109306

[^1_10]: https://www.reddit.com/r/CloudFlare/comments/1gx8y1x/is_it_possible_to_search_cloudflare_for_a/

[^1_11]: https://developers.cloudflare.com/registrar/top-level-domains/

[^1_12]: https://help.webflow.com/hc/en-us/articles/33961239562387-Manually-connect-a-custom-domain


---

# behind domain.tld there is an AWS cloudfront + bucket with a static landing page. So how should I configure my cloudflare DNS ?

For your AWS CloudFront + S3 setup with Cloudflare DNS, you need to configure DNS records differently for the root domain versus the www subdomain because of DNS protocol limitations.[^2_1]

## DNS Configuration for Both Domains

**For www.domain.tld (subdomain):**

- Type: CNAME
- Name: `www`
- Target: Your CloudFront distribution domain (e.g., `d111111abcdef8.cloudfront.net`)
- Proxy status: **DNS only** (grey cloud)[^2_2][^2_3]

**For domain.tld (root/apex domain):**

- Type: CNAME
- Name: `@`
- Target: Your CloudFront distribution domain
- Proxy status: **DNS only** (grey cloud)[^2_2]

Cloudflare automatically handles **CNAME flattening** for root domains, which resolves the technical limitation that normally prevents CNAME records at the apex domain. This feature is enabled by default and converts the CNAME to an A record behind the scenes.[^2_4][^2_5]

## Important CloudFront Configuration

Before adding these DNS records, ensure your CloudFront distribution has both domain names listed in the **Alternate Domain Names (CNAMEs)** field:[^2_3][^2_2]

- `domain.tld`
- `www.domain.tld`

You also need a valid SSL/TLS certificate from AWS Certificate Manager (ACM) that covers both domains attached to your CloudFront distribution.[^2_6][^2_2]

## Why DNS Only Mode

Keep the proxy status as "DNS only" (not proxied through Cloudflare) to avoid double-proxying, since CloudFront already provides CDN functionality. Proxying through both services can cause SSL certificate conflicts and routing issues.[^2_2]
<span style="display:none">[^2_10][^2_7][^2_8][^2_9]</span>

<div align="center">â‚</div>

[^2_1]: https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/add-domain-existing-distribution.html

[^2_2]: https://advancedweb.hu/how-to-use-a-custom-domain-on-cloudfront-with-cloudflare-managed-dns/

[^2_3]: https://www.reddit.com/r/aws/comments/4ina9r/cloudfront_cdn_cloudflare_dns_cdn/

[^2_4]: https://www.skynats.com/blog/cloudflare-cname-flattening/

[^2_5]: https://developers.cloudflare.com/dns/cname-flattening/set-up-cname-flattening/

[^2_6]: https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/CNAMEs.html

[^2_7]: https://mikefallows.com/posts/add-a-custom-url-to-cloudfront-with-cloudflare/

[^2_8]: https://builder.aws.com/content/2xDn623NDrEyYmca0yBoTx4g0t3/how-i-deployed-my-portfolio-using-aws-s3-cloudfront-cloudflare-free-ssl-and-email

[^2_9]: https://kinsta.com/docs/wordpress-hosting/wordpress-cdn/cloudfront/

[^2_10]: https://www.youtube.com/watch?v=eLBZQyZhHFo


---

# for my CNAME @ record. What should I do for proxy status ? Proxied or not ?

For your CloudFront + S3 setup, you should set the proxy status to **DNS only** (grey cloud, not proxied) for your CNAME @ record.[^3_1][^3_2]

## Why DNS Only Is Recommended

Using "Proxied" (orange cloud) creates a **double-CDN setup** where traffic goes through Cloudflare's CDN first, then to CloudFront's CDN. This configuration causes several issues:[^3_3][^3_4]

- **TLS/SSL certificate conflicts**: AWS ACM certificates don't work properly when Cloudflare sits in front of CloudFront, leading to TLS handshake failures and Cloudflare error pages[^3_3]
- **Double caching redundancy**: Both services cache your content, which provides no meaningful benefit and can cause cache synchronization issues[^3_5][^3_3]
- **Unnecessary complexity**: Since CloudFront already provides CDN, DDoS protection via AWS Shield, and global edge locations, adding Cloudflare proxy adds another layer without significant advantages[^3_4]


## When Proxied Might Be Considered

The only scenario where proxied mode makes sense is if you specifically want Cloudflare's WAF features, "Under Attack" mode, or prefer Cloudflare's DDoS protection over AWS Shield. However, this requires disabling CloudFront entirely and connecting Cloudflare directly to S3 instead.[^3_3]

For your current architecture (CloudFront â†’ S3), keep both your `@` and `www` CNAME records set to **DNS only** to avoid conflicts and maintain proper SSL/TLS functionality.[^3_1]
<span style="display:none">[^3_10][^3_11][^3_12][^3_6][^3_7][^3_8][^3_9]</span>

<div align="center">â‚</div>

[^3_1]: https://advancedweb.hu/how-to-use-a-custom-domain-on-cloudfront-with-cloudflare-managed-dns/

[^3_2]: https://www.reddit.com/r/aws/comments/4ina9r/cloudfront_cdn_cloudflare_dns_cdn/

[^3_3]: https://www.reddit.com/r/CloudFlare/comments/1hvsj3l/can_i_combine_cloudflare_proxied_service_and_aws/

[^3_4]: https://stackoverflow.com/questions/43824777/whats-the-benefit-of-using-both-cloudfront-and-cloudflare

[^3_5]: https://www.reddit.com/r/aws/comments/ycbmzq/cdn_stacking_with_cloudflare_infront_of_cloudfront/

[^3_6]: https://mikefallows.com/posts/add-a-custom-url-to-cloudfront-with-cloudflare/

[^3_7]: https://www.cloudflare.com/cloudflare-vs-cloudfront/

[^3_8]: https://www.azuredevopsguide.com/what-is-the-difference-between-proxied-and-dns-only/

[^3_9]: https://meta.discourse.org/t/cloudflare-proxy-orange-cloud-causing-uploading-file-fail-aws-s3/227871

[^3_10]: https://cloudflare-docs-zh.pages.dev/dns/manage-dns-records/reference/proxied-dns-records/

[^3_11]: https://www.reddit.com/r/openwrt/comments/sdx2cf/debugging_cloudflare_proxy_orange_cloud/

[^3_12]: https://mail.asworldglobal.com/swjt/cloudflare-proxy-vs-dns-only.html
