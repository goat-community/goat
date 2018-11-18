<?xml version="1.0" encoding="UTF-8"?><sld:StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:sld="http://www.opengis.net/sld" xmlns:gml="http://www.opengis.net/gml" xmlns:ogc="http://www.opengis.net/ogc" version="1.0.0">
  <sld:NamedLayer>
    <sld:Name>grid_100</sld:Name>
    <sld:UserStyle>
      <sld:Name>grid_100</sld:Name>
      <sld:FeatureTypeStyle>
        <sld:Name>name</sld:Name>
                <sld:Rule>
          <sld:Name>0</sld:Name>
          <ogc:Filter>
            <ogc:And>
              <ogc:PropertyIsGreaterThan>
                <ogc:PropertyName>percentile</ogc:PropertyName>
                <ogc:Literal>0</ogc:Literal>
              </ogc:PropertyIsGreaterThan>
              <ogc:PropertyIsLessThanOrEqualTo>
                <ogc:PropertyName>percentile</ogc:PropertyName>
                <ogc:Literal>1</ogc:Literal>
              </ogc:PropertyIsLessThanOrEqualTo>
            </ogc:And>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#f7fbff</sld:CssParameter>
              <sld:CssParameter name="fill-opacity">0.4</sld:CssParameter>
            </sld:Fill>
            <!--
            <sld:Stroke>
              <sld:CssParameter name="stroke">#000001</sld:CssParameter>
              <sld:CssParameter name="stroke-linejoin">bevel</sld:CssParameter>
              <sld:CssParameter name="stroke-width">0.00000</sld:CssParameter>
            </sld:Stroke>
			-->
          </sld:PolygonSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>1</sld:Name>
          <ogc:Filter>
            <ogc:And>
              <ogc:PropertyIsGreaterThanOrEqualTo>
                <ogc:PropertyName>percentile</ogc:PropertyName>
                <ogc:Literal>1</ogc:Literal>
              </ogc:PropertyIsGreaterThanOrEqualTo>
              <ogc:PropertyIsLessThanOrEqualTo>
                <ogc:PropertyName>percentile</ogc:PropertyName>
                <ogc:Literal>2</ogc:Literal>
              </ogc:PropertyIsLessThanOrEqualTo>
            </ogc:And>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#f7fbff</sld:CssParameter>
              <sld:CssParameter name="fill-opacity">0.4</sld:CssParameter>
            </sld:Fill>
            <!--
            <sld:Stroke>
              <sld:CssParameter name="stroke">#000001</sld:CssParameter>
              <sld:CssParameter name="stroke-linejoin">bevel</sld:CssParameter>
              <sld:CssParameter name="stroke-width">0.00000</sld:CssParameter>
            </sld:Stroke>
			-->
          </sld:PolygonSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>2</sld:Name>
          <ogc:Filter>
            <ogc:And>
              <ogc:PropertyIsGreaterThan>
                <ogc:PropertyName>percentile</ogc:PropertyName>
                <ogc:Literal>2</ogc:Literal>
              </ogc:PropertyIsGreaterThan>
              <ogc:PropertyIsLessThanOrEqualTo>
                <ogc:PropertyName>percentile</ogc:PropertyName>
                <ogc:Literal>3</ogc:Literal>
              </ogc:PropertyIsLessThanOrEqualTo>
            </ogc:And>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#c7dcef</sld:CssParameter>
              <sld:CssParameter name="fill-opacity">0.4</sld:CssParameter>
            </sld:Fill>
            <!--
            <sld:Stroke>
              <sld:CssParameter name="stroke">#000001</sld:CssParameter>
              <sld:CssParameter name="stroke-linejoin">bevel</sld:CssParameter>
              <sld:CssParameter name="stroke-width">0.00000</sld:CssParameter>
            </sld:Stroke>
			-->
          </sld:PolygonSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>3</sld:Name>
          <ogc:Filter>
            <ogc:And>
              <ogc:PropertyIsGreaterThan>
                <ogc:PropertyName>percentile</ogc:PropertyName>
                <ogc:Literal>3</ogc:Literal>
              </ogc:PropertyIsGreaterThan>
              <ogc:PropertyIsLessThanOrEqualTo>
                <ogc:PropertyName>percentile</ogc:PropertyName>
                <ogc:Literal>4</ogc:Literal>
              </ogc:PropertyIsLessThanOrEqualTo>
            </ogc:And>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#72b2d7</sld:CssParameter>
              <sld:CssParameter name="fill-opacity">0.4</sld:CssParameter>
            </sld:Fill>
            <!--
            <sld:Stroke>
              <sld:CssParameter name="stroke">#000001</sld:CssParameter>
              <sld:CssParameter name="stroke-linejoin">bevel</sld:CssParameter>
              <sld:CssParameter name="stroke-width">0.00000</sld:CssParameter>
            </sld:Stroke>
			-->
          </sld:PolygonSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>4</sld:Name>
          <ogc:Filter>
            <ogc:And>
              <ogc:PropertyIsGreaterThan>
                <ogc:PropertyName>percentile</ogc:PropertyName>
                <ogc:Literal>4</ogc:Literal>
              </ogc:PropertyIsGreaterThan>
              <ogc:PropertyIsLessThanOrEqualTo>
                <ogc:PropertyName>percentile</ogc:PropertyName>
                <ogc:Literal>5</ogc:Literal>
              </ogc:PropertyIsLessThanOrEqualTo>
            </ogc:And>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#2878b8</sld:CssParameter>
              <sld:CssParameter name="fill-opacity">0.4</sld:CssParameter>
            </sld:Fill>
            <!--
            <sld:Stroke>
              <sld:CssParameter name="stroke">#000001</sld:CssParameter>
              <sld:CssParameter name="stroke-linejoin">bevel</sld:CssParameter>
              <sld:CssParameter name="stroke-width">0.00000</sld:CssParameter>
            </sld:Stroke>
			-->
          </sld:PolygonSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>5</sld:Name>
          <ogc:Filter>
            <ogc:And>
              <ogc:PropertyIsGreaterThan>
                <ogc:PropertyName>percentile</ogc:PropertyName>
                <ogc:Literal>5</ogc:Literal>
              </ogc:PropertyIsGreaterThan>
              <ogc:PropertyIsLessThanOrEqualTo>
                <ogc:PropertyName>percentile</ogc:PropertyName>
                <ogc:Literal>6</ogc:Literal>
              </ogc:PropertyIsLessThanOrEqualTo>
            </ogc:And>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#08306b</sld:CssParameter>
              <sld:CssParameter name="fill-opacity">0.4</sld:CssParameter>
            </sld:Fill>
            <!--
            <sld:Stroke>
              <sld:CssParameter name="stroke">#000001</sld:CssParameter>
              <sld:CssParameter name="stroke-linejoin">bevel</sld:CssParameter>
              <sld:CssParameter name="stroke-width">0.00000</sld:CssParameter>
            </sld:Stroke>
        	-->  
		</sld:PolygonSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </sld:NamedLayer>
</sld:StyledLayerDescriptor>