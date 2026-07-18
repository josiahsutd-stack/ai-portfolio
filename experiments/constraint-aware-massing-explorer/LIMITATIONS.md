# Limitations

## Geometry

- Rectangular sites and axis-aligned rectangular masses only.
- No terrain, easements, party walls, neighboring obstructions, cores, stairs, lifts, facade depth, structure, parking, servicing, units, or room plans.
- GFA is the sum of rectangular footprint areas multiplied by floors; exclusions and jurisdiction-specific measurement rules are not modeled.

## Codes And Professional Review

- Numeric constraints are inputs, not rules inferred from codes.
- Constraint labels do not establish that a value is current, applicable, interpreted correctly, or accepted by an authority.
- Site access is not internal egress, fire-engineering, accessibility, security, or traffic validation.
- Outputs require review by appropriately qualified design and engineering practitioners.

## Environmental Proxies

- Solar score uses facade orientation weights, not sun positions or weather data.
- Daylight score uses exposed perimeter, not windows, room depth, reflectance, shading, or illuminance.
- Wind score uses projected blockage and open ground, not CFD or pedestrian wind comfort.

## Search And Evaluation

- Search is seeded parametric sampling with Pareto filtering, not a learned model.
- The utility score depends on user weights and simplified normalized proxies.
- Three synthetic sites do not demonstrate external validity or design quality.
- A feasible candidate only passes implemented checks; unmodeled constraints may make it unusable.

## Visuals

SVG plans and isometric diagrams are generated from candidate rectangles. They are explanatory artifacts, not architectural drawings, BIM models, renders, or evidence of a constructed design.
