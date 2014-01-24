from zinc import ZincRequestProcessor

payload = {
  "client_token": "public",
  "retailer": "amazon",
  "product_url": "http://www.amazon.com/gp/product/0394800761"
}
result = ZincRequestProcessor.process("variant_options", payload)
print result

