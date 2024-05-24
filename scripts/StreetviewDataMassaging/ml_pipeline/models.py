### Author: Ashlynn Wimer
### Date: 5/23/2024
### About: This script is used to gauge the performance of a few basic ML models
###        on predicting the depressingness or liveliness of images based on their
###        segments. If they do well, I'll create a second script using the best 
###        performer to generalize the models; otherwise, I'll decline to use this
###        dataset for now. 

from pyspark.sql import SparkSession
from pyspark.ml import Pipeline
from pyspark.ml.regression import LinearRegression, RandomForestRegressor
from pyspark.ml.feature import VectorAssembler, RobustScaler
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder
import pyspark.sql.functions as F
import numpy as np

spark = SparkSession.builder.getOrCreate()

# Get data
depressing_scores = spark.read.option('header', True)\
    .csv('../../../data/raw/qscores.tsv', sep='\t')

depressing_scores = depressing_scores\
    .filter((F.col('study_id') == '50f62ccfa84ea7c5fdd2e459'))\
    [['location_id', 'trueskill_score']]\
    .withColumnRenamed(existing='trueskill_score', new='depressingness_score')

depressing_scores = depressing_scores.withColumn('depressingness_score', depressing_scores['depressingness_score'].cast('float'))

livelier_scores = spark.read.option('header', True)\
    .csv('../../../data/raw/qscores.tsv', sep='\t')

livelier_scores = livelier_scores\
    .filter((F.col('study_id') == '50f62c41a84ea7c5fdd2e454'))\
    [['location_id', 'trueskill_score']]\
    .withColumnRenamed(existing='trueskill_score', new='liveliness_score')

livelier_scores = livelier_scores.withColumn('liveliness_score', livelier_scores['liveliness_score'].cast('float'))

pp_segs = spark.read.parquet('../../../data/raw/place_pulse_segments.parquet')\
                    .withColumn('location_id',
                        F.split(
                            F.col('__index_level_0__'), '_'
                        )[2])\
                    .drop('__index_level_0__')

# Merge
labeled_segs = pp_segs\
                    .join(livelier_scores, on='location_id', how='right')\
                    .join(depressing_scores, on='location_id', how='right')

# We use 18 features selected due to their prominence.
features = ['road', 'sky', 'tree', 'building', 'grass', 'car', 'sidewalk', 'wall', 'earth', 'fence', 'plant', 'field', 'path', 'house', 'ceiling', 'floor', 'signboard', 'truck']
assembler = VectorAssembler(
    inputCols=features,
    outputCol='features',
    handleInvalid='skip'
)

# But we scale them
scaler = RobustScaler(
    inputCol='features',
    outputCol='scaledFeatures'
)

# Models
lively_lir = LinearRegression(featuresCol='scaledFeatures', labelCol='liveliness_score')
depressing_lir = LinearRegression(featuresCol='scaledFeatures', labelCol='depressingness_score')

lively_rf = RandomForestRegressor(featuresCol='scaledFeatures', labelCol='liveliness_score')
depressing_rf = RandomForestRegressor(featuresCol='scaledFeatures', labelCol='depressingness_score')

# Pipelines
lively_lir_pipeline = Pipeline(stages=[assembler, scaler, lively_lir])
depressing_lir_pipeline = Pipeline(stages=[assembler, scaler, depressing_lir])

lively_rf_pipeline = Pipeline(stages=[assembler, scaler, lively_rf])
depressing_rf_pipeline = Pipeline(stages=[assembler, scaler, depressing_rf])

# Param grids
lively_lir_params = ParamGridBuilder()\
    .addGrid(lively_lir.regParam, [0, .5])\
    .addGrid(lively_lir.elasticNetParam, [0, 1])\
    .build()

depressing_lir_params = ParamGridBuilder()\
    .addGrid(depressing_lir.regParam, [0, .5])\
    .addGrid(depressing_lir.elasticNetParam, [0, 1])\
    .build()
    
lively_rf_params = ParamGridBuilder()\
    .addGrid(lively_rf.maxDepth, [10, 15])\
    .addGrid(lively_rf.numTrees, [150, 200])\
    .build()

depressing_rf_params = ParamGridBuilder()\
    .addGrid(depressing_rf.maxDepth, [10, 15])\
    .addGrid(depressing_rf.numTrees, [150, 200])\
    .build()

# evaluators
lively_evaluator = RegressionEvaluator(labelCol='liveliness_score')
depressing_evaluator = RegressionEvaluator(labelCol='depressingness_score')

# crossvals for 5 fold cross val
lively_lir_cv = CrossValidator(estimator=lively_lir_pipeline,
                              estimatorParamMaps=lively_lir_params,
                              evaluator=lively_evaluator,
                              numFolds=5)

lively_rf_cv = CrossValidator(estimator=lively_rf_pipeline,
                              estimatorParamMaps=lively_rf_params,
                              evaluator=lively_evaluator,
                              numFolds=5)

depressing_lir_cv = CrossValidator(estimator=depressing_lir_pipeline,
                              estimatorParamMaps=depressing_lir_params,
                              evaluator=depressing_evaluator,
                              numFolds=5)

depressing_rf_cv = CrossValidator(estimator=depressing_rf_pipeline,
                              estimatorParamMaps=depressing_rf_params,
                              evaluator=depressing_evaluator,
                              numFolds=5)

# split data
train, test = labeled_segs.randomSplit([0.8, 0.2], seed=42)
train.persist()
test.persist()

# CVs
lively_lir_cv = lively_lir_cv.fit(train)
lively_rf_cv = lively_rf_cv.fit(train)
depressing_lir_cv = depressing_lir_cv.fit(train)
depressing_rf_cv = depressing_rf_cv.fit(train)

# Evaluate performance
lively_lir_rmse = lively_evaluator.evaluate(lively_lir_cv.transform(test))
lively_rf_rmse = lively_evalator.evaluate(lively_rf_cv.transform(test))
depressing_lir_rmse = depressing_evaluator.evaluate(depressing_lir_cv.transform(test))
depressing_rf_rmse = depressing_evalator.evaluate(depressing_rf_cv.transform(test))

#Report metrics
print('========================')
print('-- Lively Performances --')
print(f'Best RMSE for Linear Regression: {lively_lir_rmse}')
print(f'Best RMSE for RF Regression: {lively_rf_rmse}')
print('-- Depressing Performances --')
print(f'Best RMSE for Linear Regression: {depressing_lir_rmse}')
print(f'Best RMSE for RF Regression: {depressing_rf_rmse}')
print('===========================')
