<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:ogc="http://www.opengis.net/ogc" xmlns="http://www.opengis.net/sld" xsi:schemaLocation="http://www.opengis.net/sld StyledLayerDescriptor.xsd" version="1.0.0">
  <NamedLayer>
    <Name>surface</Name>
    <UserStyle>
      <Name>surface</Name>
      <FeatureTypeStyle>
        <Rule>
          <Name>no data</Name>
            <Title>
              no data
                <Localized lang="al">unclassified (albanian)</Localized>
				<Localized lang="ar">unclassified (arabian)</Localized>
            	<Localized lang="cn">unclassified (chinese)</Localized>
				<Localized lang="de">keine Daten</Localized>
            	<Localized lang="en">no data</Localized>
				<Localized lang="es">ningún datos</Localized>
            	<Localized lang="fr">pas de données</Localized>
          	</Title>
          <LineSymbolizer>
            <Stroke>
              <CssParameter name="stroke">#999999</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
              <CssParameter name="stroke-linecap">square</CssParameter>
            </Stroke>
          </LineSymbolizer>
        </Rule>
        <Rule>
          <Name>
            asphalt
                <Localized lang="al">asphalt (albanian)</Localized>
				<Localized lang="ar">asphalt (arabian)</Localized>
            	<Localized lang="cn">asphalt (chinese)</Localized>
				<Localized lang="de">Asphalt</Localized>
            	<Localized lang="en">asphalt</Localized>
				<Localized lang="es">asphalt (spanish)</Localized>
            	<Localized lang="fr">asphalt (frensh)</Localized>
          </Name>
            <Title>asphalt</Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
             <ogc:Or>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>surface</ogc:PropertyName>
              <ogc:Literal>asphalt</ogc:Literal>
            </ogc:PropertyIsEqualTo>
             <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>surface</ogc:PropertyName>
              <ogc:Literal>paved</ogc:Literal>
            </ogc:PropertyIsEqualTo>
               </ogc:Or>
          </ogc:Filter>
          <LineSymbolizer>
            <Stroke>
              <CssParameter name="stroke">#000000</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
              <CssParameter name="stroke-linecap">square</CssParameter>
            </Stroke>
          </LineSymbolizer>
        </Rule>
        <Rule>
          <Name>concrete</Name>
            <Title>
              concrete
                <Localized lang="al">concrete (albanian)</Localized>
				<Localized lang="ar">concrete (arabian)</Localized>
            	<Localized lang="cn">concrete (chinese)</Localized>
				<Localized lang="de">Beton</Localized>
            	<Localized lang="en">concrete</Localized>
				<Localized lang="es">concrete (spanish)</Localized>
            	<Localized lang="fr">concrete (frensh)</Localized>
          	</Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:Or>
              <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>surface</ogc:PropertyName>
                <ogc:Literal>concrete</ogc:Literal>
              </ogc:PropertyIsEqualTo>
              <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>surface</ogc:PropertyName>
                <ogc:Literal>concrete:plates</ogc:Literal>
              </ogc:PropertyIsEqualTo>
            </ogc:Or>
          </ogc:Filter>
          <LineSymbolizer>
            <Stroke>
              <CssParameter name="stroke">#266bca</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
              <CssParameter name="stroke-linecap">square</CssParameter>
            </Stroke>
          </LineSymbolizer>
        </Rule>
        <Rule> 
          <Name>ground or gravel</Name>
            <Title>
              ground or gravel
                <Localized lang="al">ground or gravel (albanian)</Localized>
				<Localized lang="ar">ground or gravel (arabian)</Localized>
            	<Localized lang="cn">ground or gravel (chinese)</Localized>
				<Localized lang="de">Erd- / Kiesweg</Localized>
            	<Localized lang="en">ground or gravel</Localized>
				<Localized lang="es">ground or gravel (spanish)</Localized>
            	<Localized lang="fr">ground or gravel (frensh)</Localized>
          	</Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:Or>
              <ogc:Or>
                <ogc:PropertyIsEqualTo>
                  <ogc:PropertyName>surface</ogc:PropertyName>
                  <ogc:Literal>dirt</ogc:Literal>
                </ogc:PropertyIsEqualTo>
                <ogc:PropertyIsEqualTo>
                  <ogc:PropertyName>surface</ogc:PropertyName>
                  <ogc:Literal>earth</ogc:Literal>
                </ogc:PropertyIsEqualTo>
              </ogc:Or>
              <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>surface</ogc:PropertyName>
                <ogc:Literal>ground</ogc:Literal>
              </ogc:PropertyIsEqualTo>
              <ogc:PropertyIsEqualTo>
               <ogc:PropertyName>surface</ogc:PropertyName>
              <ogc:Literal>mud</ogc:Literal>
            </ogc:PropertyIsEqualTo>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>surface</ogc:PropertyName>
              <ogc:Literal>unpaved</ogc:Literal>
            </ogc:PropertyIsEqualTo>
              <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>surface</ogc:PropertyName>
              <ogc:Literal>sand</ogc:Literal>
            </ogc:PropertyIsEqualTo>
                            <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>surface</ogc:PropertyName>
                <ogc:Literal>fine_gravel</ogc:Literal>
              </ogc:PropertyIsEqualTo>
              <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>surface</ogc:PropertyName>
                <ogc:Literal>gravel</ogc:Literal>
              </ogc:PropertyIsEqualTo>
              <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>surface</ogc:PropertyName>
              <ogc:Literal>compacted</ogc:Literal>
            </ogc:PropertyIsEqualTo>
                          <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>surface</ogc:PropertyName>
              <ogc:Literal>pebblestone</ogc:Literal>
            </ogc:PropertyIsEqualTo>
            </ogc:Or>
          </ogc:Filter>
          <LineSymbolizer>
            <Stroke>
              <CssParameter name="stroke">#ad7940</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
              <CssParameter name="stroke-linecap">square</CssParameter>
            </Stroke>
          </LineSymbolizer>
        </Rule>
        <Rule>
          <Name>grass</Name>
            <Title>
              grass or grass paver
                <Localized lang="al">grass</Localized>
				<Localized lang="ar">grass (arabian)</Localized>
            	<Localized lang="cn">grass (chinese)</Localized>
				<Localized lang="de">Grass</Localized>
            	<Localized lang="en">grass</Localized>
				<Localized lang="es">grass (spanish)</Localized>
            	<Localized lang="fr">grass (frensh)</Localized>
          	</Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:Or>
              <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>surface</ogc:PropertyName>
                <ogc:Literal>grass</ogc:Literal>
              </ogc:PropertyIsEqualTo>
              <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>surface</ogc:PropertyName>
                <ogc:Literal>grass_paver</ogc:Literal>
              </ogc:PropertyIsEqualTo>
            </ogc:Or>
          </ogc:Filter>
          <LineSymbolizer>
            <Stroke>
              <CssParameter name="stroke">#0cae3f</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
              <CssParameter name="stroke-linecap">square</CssParameter>
            </Stroke>
          </LineSymbolizer>
        </Rule>
        <Rule>
          <Name>paving stones</Name>
            <Title>
              paving stones
                <Localized lang="al">paving stones (albanian)</Localized>
				<Localized lang="ar">paving stones (arabian)</Localized>
            	<Localized lang="cn">paving stones (chinese)</Localized>
				<Localized lang="de">Pflastersteine</Localized>
            	<Localized lang="en">paving stones</Localized>
				<Localized lang="es">paving stones (spanish)</Localized>
            	<Localized lang="fr">paving stones (frensh)</Localized>
          	</Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:Or>
              <ogc:Or>
                <ogc:PropertyIsEqualTo>
                  <ogc:PropertyName>surface</ogc:PropertyName>
                  <ogc:Literal>paving_stones</ogc:Literal>
                </ogc:PropertyIsEqualTo>
                <ogc:PropertyIsEqualTo>
                  <ogc:PropertyName>surface</ogc:PropertyName>
                  <ogc:Literal>paving_stones:30</ogc:Literal>
                </ogc:PropertyIsEqualTo>
                              <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>surface</ogc:PropertyName>
                <ogc:Literal>cobblestone</ogc:Literal>
              </ogc:PropertyIsEqualTo>
              <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>surface</ogc:PropertyName>
                <ogc:Literal>cobblestone:flattened</ogc:Literal>
              </ogc:PropertyIsEqualTo>
              </ogc:Or>
              <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>surface</ogc:PropertyName>
                <ogc:Literal>sett</ogc:Literal>
              </ogc:PropertyIsEqualTo>
            </ogc:Or>
          </ogc:Filter>
          <LineSymbolizer>
            <Stroke>
              <CssParameter name="stroke">#32c9ea</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
              <CssParameter name="stroke-linecap">square</CssParameter>
            </Stroke>
          </LineSymbolizer>
        </Rule>
      </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>