#!/usr/bin/env python

import sys
import boto3
from pprint import pprint


def update_website_configuration(s3, build, bucket="api.hearthstonejson.com"):
	print("Querying website configuration for %r" % (bucket))
	orig_config = s3.get_bucket_website(Bucket=bucket)
	pprint(orig_config)

	if "ResponseMetadata" in orig_config:
		del orig_config["ResponseMetadata"]

	config = orig_config.copy()

	config["RoutingRules"] = [{
		"Condition": {
			"KeyPrefixEquals": "v1/latest/"
		},
		"Redirect": {
			"ReplaceKeyPrefixWith": "v1/%i/" % (build),
			"HttpRedirectCode": "302",
			"Protocol": "https",
		},
	}]

	if config != orig_config:
		print("Updating website configuration")
		pprint(config)
		s3.put_bucket_website(Bucket=bucket, WebsiteConfiguration=config)
	else:
		print("Website configuration up-to-date")


def update_art_404_redirects(s3, bucket="art.hearthstonejson.com"):
	orig_config = s3.get_bucket_website(Bucket=bucket)

	if "ResponseMetadata" in orig_config:
		del orig_config["ResponseMetadata"]

	config = orig_config.copy()

	prefixes = [
		("v1/orig/", "png"),
		("v1/tiles/", "png"),
		("v1/256x/", "jpg"),
		("v1/512x/", "jpg"),
	]

	config["RoutingRules"] = []

	for prefix, ext in prefixes:
		config["RoutingRules"].append({
			"Condition": {
				"HttpErrorCodeReturnedEquals": "404",
				"KeyPrefixEquals": prefix,
			},
			"Redirect": {
				"ReplaceKeyWith": prefix + "XXX_001.%s" % (ext),
				"HttpRedirectCode": "302",
				"Protocol": "https",
			}
		})

	if config != orig_config:
		print("Updating 404 redirects")
		pprint(config)
		s3.put_bucket_website(Bucket=bucket, WebsiteConfiguration=config)
	else:
		print("404 redirects up-to-date")


def main():
	build = int(sys.argv[1])
	s3 = boto3.client("s3")
	update_website_configuration(s3, build)
	update_art_404_redirects(s3)


if __name__ == "__main__":
	main()
