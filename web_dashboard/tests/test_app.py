import importlib.util, pathlib, sys, tempfile, types, unittest
APP=pathlib.Path(__file__).resolve().parents[1]/'app.py'
spec=importlib.util.spec_from_file_location('iris_app',APP); app=importlib.util.module_from_spec(spec); sys.modules['iris_app']=app; spec.loader.exec_module(app)
class AppTests(unittest.TestCase):
 def test_report_registry_has_ten(self): self.assertEqual(len(app.REPORTS_REGISTRY),10)
 def test_measurements_are_four(self): self.assertEqual(len(app.MEASUREMENTS),4)
 def test_ask_unsupported_is_rejected_without_database(self):
  out=app.ask_iris('Can you identify a new flower from a photograph?')
  self.assertFalse(out['validated']); self.assertEqual(out['status'],'REJECTED')
 def test_ask_threshold_uses_parameter(self):
  original=app.rows; calls=[]
  app.rows=lambda sql,params=None: calls.append((sql,params)) or [{'specimen_id':7}]
  try:
   out=app.ask_iris('Show specimens with petal length above 5 cm')
   self.assertTrue(out['validated']); self.assertEqual(calls[0][1],{'threshold':5.0})
   self.assertIn('%(threshold)s',calls[0][0])
  finally: app.rows=original
 def test_r10_report_uses_existing_app_sql_and_parameter_binding(self):
  p=app.REPORTS/'R10_filtered_specimen_explorer_app.sql'
  self.assertTrue(p.exists())
  sql=p.read_text(); self.assertIn(':species_name',sql)
  converted=__import__('re').sub(r':([a-zA-Z_][a-zA-Z0-9_]*)',r'%(\1)s',sql)
  self.assertIn('%(',converted)
 def test_ask_variability_question_is_supported(self):
  original=app.rows; app.rows=lambda sql,params=None: [{'species_name':'Iris-virginica','sd_petal_length_cm':0.55}]
  try:
   out=app.ask_iris('Which species has the greatest petal length variability?')
   self.assertEqual(out['intent'],'petal_variability'); self.assertTrue(out['validated'])
  finally: app.rows=original
 def test_overview_kpis_are_derived_from_species_rows(self):
  original_rows, original_quality=app.rows, app.quality_data
  sample=[
   {'species_name':'Iris-setosa','specimen_count':50,'avg_sepal_length_cm':5.01,'avg_sepal_width_cm':3.43,'avg_petal_length_cm':1.46,'avg_petal_width_cm':0.25,'min_sepal_length_cm':4.3,'max_sepal_length_cm':5.8,'min_sepal_width_cm':2.3,'max_sepal_width_cm':4.4,'min_petal_length_cm':1.0,'max_petal_length_cm':1.9,'min_petal_width_cm':0.1,'max_petal_width_cm':0.6,'sd_sepal_length_cm':0.35,'sd_sepal_width_cm':0.38,'sd_petal_length_cm':0.17,'sd_petal_width_cm':0.10},
   {'species_name':'Iris-versicolor','specimen_count':50,'avg_sepal_length_cm':5.94,'avg_sepal_width_cm':2.77,'avg_petal_length_cm':4.26,'avg_petal_width_cm':1.33,'min_sepal_length_cm':4.9,'max_sepal_length_cm':7.0,'min_sepal_width_cm':2.0,'max_sepal_width_cm':3.4,'min_petal_length_cm':3.0,'max_petal_length_cm':5.1,'min_petal_width_cm':1.0,'max_petal_width_cm':1.8,'sd_sepal_length_cm':0.52,'sd_sepal_width_cm':0.31,'sd_petal_length_cm':0.47,'sd_petal_width_cm':0.20},
   {'species_name':'Iris-virginica','specimen_count':50,'avg_sepal_length_cm':6.59,'avg_sepal_width_cm':2.97,'avg_petal_length_cm':5.55,'avg_petal_width_cm':2.03,'min_sepal_length_cm':4.9,'max_sepal_length_cm':7.9,'min_sepal_width_cm':2.2,'max_sepal_width_cm':3.8,'min_petal_length_cm':4.5,'max_petal_length_cm':6.9,'min_petal_width_cm':1.4,'max_petal_width_cm':2.5,'sd_sepal_length_cm':0.63,'sd_sepal_width_cm':0.32,'sd_petal_length_cm':0.55,'sd_petal_width_cm':0.27},
  ]
  app.rows=lambda sql,params=None: sample
  app.quality_data=lambda quick=False: {}
  try:
   d=app.overview_data()
   self.assertEqual(d['total'],150)
   self.assertEqual([x['value'] for x in d['kpis'][:5]],[150,3,4,50,50])
   self.assertEqual(d['kpis'][5]['value'],10)
   self.assertEqual(d['insights'][0]['species'],'Iris-virginica')
  finally: app.rows, app.quality_data=original_rows, original_quality
 def test_json_safe_decimal(self):
  from decimal import Decimal
  self.assertEqual(app.json_safe(Decimal('2.50')),2.5)
if __name__=='__main__': unittest.main(verbosity=2)
