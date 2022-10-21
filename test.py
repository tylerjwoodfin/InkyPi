from securedata import securedata

# price = securedata.getFileAsArray("BTC_LATEST_PRICE", ignoreNotFound=True)
# print(price)
# print(price[0])


print(float(['19058.60000'][0]))
# print(f"BTC ${str('{:,.2f}'.format(float(['19058.60000'])))}")

# securedata.writeFile("BTC_LATEST_PRICE", content=['19058.60000'][0])