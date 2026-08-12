import os, tempfile, unittest
from pathlib import Path
os.environ['DATABASE_PATH']=str(Path(tempfile.mkdtemp())/'test.db')
from backend.app import init_db, conn, score, understand, TRANSITIONS
class CoreTests(unittest.TestCase):
 def setUp(self): init_db()
 def test_priority_is_explainable(self):
  total,p,s,r=score('Waste Management','unsafe overflow near school','5 days'); self.assertGreaterEqual(total,60); self.assertIn('Severity=',r); self.assertEqual(p,'CRITICAL') if total>=80 else None
 def test_multilingual_understanding(self): self.assertEqual(understand('Complaint','5 din se kachra nahi utha','Other','Ward 17')['category'],'Waste Management')
 def test_transition_guard(self): self.assertNotIn('RESOLVED',TRANSITIONS['SUBMITTED']); self.assertIn('AI_ANALYZING',TRANSITIONS['SUBMITTED'])
if __name__=='__main__': unittest.main()
