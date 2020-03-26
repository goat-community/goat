<?xml version="1.0" encoding="UTF-8"?><sld:StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:sld="http://www.opengis.net/sld" xmlns:gml="http://www.opengis.net/gml" xmlns:ogc="http://www.opengis.net/ogc" version="1.0.0">
  <sld:NamedLayer>
    <sld:Name>line</sld:Name>
    <sld:UserStyle>
      <sld:Name>line</sld:Name>
      <sld:Title>Default Line</sld:Title>
      <sld:IsDefault>1</sld:IsDefault>
      <sld:Abstract>A sample style that draws a line</sld:Abstract>
      <sld:FeatureTypeStyle>
        <sld:Name>name</sld:Name>
        <sld:Rule>
          <sld:Name>rule1</sld:Name>
          <sld:Title>Blue Line</sld:Title>
          <sld:Abstract>A solid blue line with a 1 pixel width</sld:Abstract>
          <ogc:Filter>
            <ogc:PropertyIsGreaterThan>
              <ogc:PropertyName>length_m</ogc:PropertyName>
              <ogc:Literal>200</ogc:Literal>
            </ogc:PropertyIsGreaterThan>
          </ogc:Filter>
          <sld:LineSymbolizer>
            <sld:Stroke>
              <sld:CssParameter name="stroke">#FF8000</sld:CssParameter>
            </sld:Stroke>
          </sld:LineSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </sld:NamedLayer>
</sld:StyledLayerDescriptor>

