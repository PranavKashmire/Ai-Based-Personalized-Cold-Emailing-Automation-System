import sys, traceback, logging
logging.disable(logging.CRITICAL)
sys.path.insert(0,'.')
import pdf_generator as pg

dummy = {
    'store_url': 'https://ex.com',
    'store_name': 'Ex Store',
    'niche': 'Fashion',
    'overall_score': 58.5,
    'categories': [
        {'category': 'SEO', 'score': 50, 'issues': [
            {'problem': 'Missing meta', 'impact': 'Medium', 'fix': 'Add it', 'type': 'Quick Win', 'revenue_impact': 'Better CTR'}
        ]}
    ],
    'top_10_improvements': [
        {'problem': 'No hero', 'impact': 'High', 'fix': 'Add hero', 'type': 'Quick Win', '_category': 'Home', 'revenue_impact': '+15%'}
    ],
    'hidden_opportunities': [
        {'problem': 'No loyalty', 'impact': 'Medium', 'fix': 'Add Smile.io', 'type': 'Long-term', 'revenue_impact': '+67% LTV'}
    ]
}

from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.pagesizes import A4
import os
from config import PDF_DIR

pdf_path = os.path.join(PDF_DIR, 'debug_test.pdf')
doc = SimpleDocTemplate(pdf_path, pagesize=A4,
                        leftMargin=pg.MARGIN, rightMargin=pg.MARGIN,
                        topMargin=pg.MARGIN, bottomMargin=20*pg.mm)
styles = pg.get_styles()
story = []

print("Building story elements...")
pg.build_cover_page(story, dummy, styles)
print(f"  cover: {len(story)} items")
pg.build_score_summary(story, dummy, styles)
print(f"  score summary: {len(story)} items")
for cat in dummy.get('categories', []):
    pg.build_category_section(story, cat, styles)
print(f"  categories: {len(story)} items")
pg.build_top10(story, dummy, styles)
print(f"  top10: {len(story)} items")
pg.build_hidden_opportunities(story, dummy, styles)
print(f"  hidden opps: {len(story)} items")
pg.build_cta_page(story, 'Ex Store', styles)
print(f"  cta: {len(story)} items")

print("\nBuilding PDF (calling doc.build)...")
try:
    doc.build(story, onFirstPage=pg.make_header_footer, onLaterPages=pg.make_header_footer)
    print(f"SUCCESS: PDF built at {pdf_path}")
except Exception as e:
    print("FULL TRACEBACK:")
    traceback.print_exc()
    print(f"\nERROR TYPE: {type(e).__name__}")
    print(f"ERROR MSG: {e}")
