# Limitations

- Mock mode does not inspect semantic image content.
- Confidence values in mock mode are workflow placeholders, not calibrated model probabilities.
- No OCR, bounding boxes, segmentation masks, or region grounding are implemented locally.
- Hosted provider mode requires credentials and a vision-capable model.
- Real VLM outputs depend on provider behavior and are not benchmarked here.
- The project demonstrates product workflow and schema boundaries, not production visual QA reliability.

## What Reviewers Should Not Infer

- Do not infer real visual reasoning from mock output.
- Do not infer defect-detection accuracy.
- Do not infer OCR capability unless a real provider returns visible text.
- Do not infer safety for construction, medical, legal, or quality-control decisions.
