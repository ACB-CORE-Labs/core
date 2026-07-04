const fs = require('fs');
const file = 'src/types/constructionEvidence.ts';
let content = fs.readFileSync(file, 'utf8');
content = content.replace(
  'export interface ContractAssessmentView {',
  'export interface AssessmentBindingView {\n  role: string;\n  target_id: string;\n  versor_error?: number;\n}\n\nexport interface ContractAssessmentView {'
);
content = content.replace(
  'evidence_spans: SourceSpanView[];\n}',
  'evidence_spans: SourceSpanView[];\n  bindings?: AssessmentBindingView[];\n}'
);
fs.writeFileSync(file, content, 'utf8');
