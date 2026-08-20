from __future__ import annotations

import argparse

from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, input_file_name, lit, sha2, struct, to_json


def transform_source(spark: SparkSession, source_name: str, raw_path: str, silver_path: str) -> None:
    raw_df = spark.read.json(raw_path)
    silver_df = (
        raw_df.dropDuplicates()
        .withColumn("_source_name", lit(source_name))
        .withColumn("_record_hash", sha2(to_json(struct(*raw_df.columns)), 256))
        .withColumn("_input_file", input_file_name())
        .withColumn("_processed_at", current_timestamp())
    )
    silver_df.write.mode("overwrite").format("delta").partitionBy("_source_name").save(f"{silver_path}/{source_name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--raw-path", required=True)
    parser.add_argument("--silver-path", required=True)
    args = parser.parse_args()

    spark = SparkSession.builder.appName(f"bronze-to-silver-{args.source}").getOrCreate()
    transform_source(spark, args.source, args.raw_path, args.silver_path)


if __name__ == "__main__":
    main()
