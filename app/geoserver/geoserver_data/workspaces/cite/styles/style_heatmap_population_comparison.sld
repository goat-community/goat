<?xml version="1.0" encoding="UTF-8"?><sld:StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:sld="http://www.opengis.net/sld" xmlns:gml="http://www.opengis.net/gml" xmlns:ogc="http://www.opengis.net/ogc" version="1.0.0">  <sld:NamedLayer>
    <sld:Name>QueryLayer</sld:Name>
    <sld:UserStyle>
      <sld:Name>QueryLayer</sld:Name>
      <sld:FeatureTypeStyle>
         <sld:Rule>
          <sld:Name>+400 inhabitants less</sld:Name>
              <Title>
              +400 inhabitants less
                <Localized lang="de">+400 Einwohner weniger</Localized>
            	<Localized lang="en">+400 inhabitants less</Localized>
              </Title>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>percentile_population</ogc:PropertyName>
              <ogc:Literal>-5</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#020950</sld:CssParameter>
              <sld:CssParameter name="fill-opacity">0.4</sld:CssParameter>
            </sld:Fill>
          </sld:PolygonSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>201 - 400 inhabitants less</sld:Name>
             <Title>
              201 - 400 inhabitants less
                <Localized lang="de">201 - 400 Einwohner weniger</Localized>
            	<Localized lang="en">201 - 400 inhabitants less</Localized>
              </Title>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>percentile_population</ogc:PropertyName>
              <ogc:Literal>4</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#343a73</sld:CssParameter>
              <sld:CssParameter name="fill-opacity">0.4</sld:CssParameter>
            </sld:Fill>
          </sld:PolygonSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>81 - 200 inhabitants less</sld:Name>
             <Title>
              81 - 200 inhabitants less
                <Localized lang="de">81 - 200 Einwohner weniger</Localized>
            	<Localized lang="en">81 - 200 inhabitants less</Localized>
              </Title>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>percentile_population</ogc:PropertyName>
              <ogc:Literal>-3</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#676b96</sld:CssParameter>
              <sld:CssParameter name="fill-opacity">0.4</sld:CssParameter>
            </sld:Fill>
          </sld:PolygonSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>21 - 80 inhabitants less</sld:Name>
             <Title>
              21 - 80 inhabitants less
                <Localized lang="de">21 - 80 Einwohner weniger</Localized>
            	<Localized lang="en">21 - 80 inhabitants less</Localized>
              </Title>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>percentile_population</ogc:PropertyName>
              <ogc:Literal>-2</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#9a9db9</sld:CssParameter>
              <sld:CssParameter name="fill-opacity">0.4</sld:CssParameter>
            </sld:Fill>
          </sld:PolygonSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>1 - 20 inhabitants less</sld:Name>
             <Title>
              1 - 20 inhabitants less
                <Localized lang="de">1 - 20 Einwohner weniger</Localized>
            	<Localized lang="en">1 - 20 inhabitants less</Localized>
              </Title>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>percentile_population</ogc:PropertyName>
              <ogc:Literal>-1</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#cdcedc</sld:CssParameter>
            </sld:Fill>
          </sld:PolygonSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>No or very small change</sld:Name>
             <Title>
              No or very small change
                <Localized lang="de">keine oder sehr kleine Änderung</Localized>
            	<Localized lang="en">No or very small changes</Localized>
              </Title>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>percentile_population</ogc:PropertyName>
              <ogc:Literal>0</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#ffffff</sld:CssParameter>
              <sld:CssParameter name="fill-opacity">0.4</sld:CssParameter>
            </sld:Fill>
          </sld:PolygonSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>1 - 20 inhabitants more</sld:Name>
             <Title>
              1 - 20 inhabitants more
                <Localized lang="de">1 - 20 Einwohner mehr</Localized>
            	<Localized lang="en">1 - 20 inhabitants more</Localized>
              </Title>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>percentile_population</ogc:PropertyName>
              <ogc:Literal>1</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#fdccb8</sld:CssParameter>
              <sld:CssParameter name="fill-opacity">0.4</sld:CssParameter>
            </sld:Fill>
          </sld:PolygonSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>21 - 80 inhabitants more</sld:Name>
             <Title>
              21 - 80 inhabitants more
                <Localized lang="de">21 - 80 Einwohner mehr</Localized>
            	<Localized lang="en">21 - 80 inhabitants more</Localized>
              </Title>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>percentile_population</ogc:PropertyName>
              <ogc:Literal>2</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#fc8f6f</sld:CssParameter>
              <sld:CssParameter name="fill-opacity">0.4</sld:CssParameter>
            </sld:Fill>
          </sld:PolygonSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>81 - 200 inhabitants</sld:Name>
             <Title>
              81 - 200 inhabitants
                <Localized lang="de">81 - 200 Einwohner mehr</Localized>
            	<Localized lang="en">81 - 200 inhabitants more</Localized>
              </Title>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>percentile_population</ogc:PropertyName>
              <ogc:Literal>3</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#f44d37</sld:CssParameter>
              <sld:CssParameter name="fill-opacity">0.4</sld:CssParameter>
            </sld:Fill>
          </sld:PolygonSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>201 - 400 inhabitants</sld:Name>
             <Title>
              201 - 400 inhabitants
                <Localized lang="de">201 - 400 Einwohner mehr</Localized>
            	<Localized lang="en">201 - 400 inhabitants more</Localized>
              </Title>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>percentile_population</ogc:PropertyName>
              <ogc:Literal>4</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#c5161b</sld:CssParameter>
              <sld:CssParameter name="fill-opacity">0.4</sld:CssParameter>
            </sld:Fill>
          </sld:PolygonSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>+400 inhabitants</sld:Name>
              <Title>
              +400 inhabitants
                <Localized lang="de">+400 Einwohner mehr</Localized>
            	<Localized lang="en">+400 inhabitants more</Localized>
              </Title>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>percentile_population</ogc:PropertyName>
              <ogc:Literal>5</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#67000d</sld:CssParameter>
              <sld:CssParameter name="fill-opacity">0.4</sld:CssParameter>
            </sld:Fill>
          </sld:PolygonSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </sld:NamedLayer>
</sld:StyledLayerDescriptor>