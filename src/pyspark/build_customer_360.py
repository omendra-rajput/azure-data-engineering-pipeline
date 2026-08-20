from __future__ import annotations

import argparse

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, max as spark_max, sum as spark_sum


def build_customer_360(spark: SparkSession, curated_root: str, output_path: str) -> None:
    accounts = spark.read.format("delta").load(f"{curated_root}/salesforce_accounts")
    charges = spark.read.format("delta").load(f"{curated_root}/stripe_charges")
    tickets = spark.read.format("delta").load(f"{curated_root}/zendesk_tickets")

    revenue = charges.groupBy("customer_id").agg(spark_sum("amount").alias("lifetime_revenue"))
    support = tickets.groupBy("customer_id").agg(
        count("*").alias("ticket_count"),
        spark_max("updated_at").alias("last_ticket_at"),
    )

    customer_360 = (
        accounts.alias("a")
        .join(revenue.alias("r"), col("a.Id") == col("r.customer_id"), "left")
        .join(support.alias("s"), col("a.Id") == col("s.customer_id"), "left")
        .select(
            col("a.Id").alias("customer_id"),
            col("a.Name").alias("customer_name"),
            col("r.lifetime_revenue"),
            col("s.ticket_count"),
            col("s.last_ticket_at"),
        )
    )

    customer_360.write.mode("overwrite").format("delta").save(output_path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--curated-root", required=True)
    parser.add_argument("--output-path", required=True)
    args = parser.parse_args()
    spark = SparkSession.builder.appName("customer-360").getOrCreate()
    build_customer_360(spark, args.curated_root, args.output_path)


if __name__ == "__main__":
    main()
