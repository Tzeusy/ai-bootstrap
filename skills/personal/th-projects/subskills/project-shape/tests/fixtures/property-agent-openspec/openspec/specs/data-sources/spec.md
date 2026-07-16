# Data Sources

Source: RFC 0001

The OneMap endpoint uses the literal URL pattern
`https://www.onemap.gov.sg/api/public/popapi/<statistic_type>?planarea=<name>&year=<year>`.

### Scenario: retrieve a named theme
- **WHEN** the client substitutes a real theme name for the URL parameter
- **THEN** it requests the corresponding OneMap theme
