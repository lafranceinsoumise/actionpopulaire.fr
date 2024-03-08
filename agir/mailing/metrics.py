from prometheus_client import Counter

ses_bounced_metric = Counter("ses_bounced_metric", "")
sendgrid_bounced_metric = Counter("sendgrid_bounced_metric", "")
