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
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>surface</ogc:PropertyName>
              <ogc:Literal>asphalt</ogc:Literal>
            </ogc:PropertyIsEqualTo>
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
          <Name>broken</Name>
            <Title>
              broken
                <Localized lang="al">broken (albanian)</Localized>
				<Localized lang="ar">broken (arabian)</Localized>
            	<Localized lang="cn">broken (chinese)</Localized>
				<Localized lang="de">beschädigte Oberfläche</Localized>
            	<Localized lang="en">broken</Localized>
				<Localized lang="es">broken (spanish)</Localized>
            	<Localized lang="fr">broken (frensh)</Localized>
          	</Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>surface</ogc:PropertyName>
              <ogc:Literal>broken</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <LineSymbolizer>
            <Stroke>
              <CssParameter name="stroke">#eb3e47</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
              <CssParameter name="stroke-linecap">square</CssParameter>
            </Stroke>
          </LineSymbolizer>
        </Rule>
        <Rule>
          <Name>cobblestone</Name>
            <Title>
              cobblestone
                <Localized lang="al">cobblestone (albanian)</Localized>
				<Localized lang="ar">cobblestone (arabian)</Localized>
            	<Localized lang="cn">cobblestone (chinese)</Localized>
				<Localized lang="de">Kopfsteinpflaster</Localized>
            	<Localized lang="en">cobblestone</Localized>
				<Localized lang="es">cobblestone (spanish)</Localized>
            	<Localized lang="fr">cobblestone (frensh)</Localized>
          	</Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:Or>
              <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>surface</ogc:PropertyName>
                <ogc:Literal>cobblestone</ogc:Literal>
              </ogc:PropertyIsEqualTo>
              <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>surface</ogc:PropertyName>
                <ogc:Literal>cobblestone:flattened</ogc:Literal>
              </ogc:PropertyIsEqualTo>
            </ogc:Or>
          </ogc:Filter>
          <LineSymbolizer>
            <Stroke>
              <CssParameter name="stroke">#696969</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
              <CssParameter name="stroke-linecap">square</CssParameter>
            </Stroke>
          </LineSymbolizer>
        </Rule>
        <Rule>
          <Name>compacted</Name>
            <Title>
              compacted
                <Localized lang="al">compacted (albanian)</Localized>
				<Localized lang="ar">compacted (arabian)</Localized>
            	<Localized lang="cn">compacted (chinese)</Localized>
				<Localized lang="de">verdichtete Schotter-Oberfläche</Localized>
            	<Localized lang="en">compacted</Localized>
				<Localized lang="es">compacted (spanish)</Localized>
            	<Localized lang="fr">compacted (frensh)</Localized>
          	</Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>surface</ogc:PropertyName>
              <ogc:Literal>compacted</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <LineSymbolizer>
            <Stroke>
              <CssParameter name="stroke">#ea9185</CssParameter>
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
          <Name>dirt, earth or ground</Name>
            <Title>
              dirt, earth or ground
                <Localized lang="al">dirt, earth or ground (albanian)</Localized>
				<Localized lang="ar">dirt, earth or ground (arabian)</Localized>
            	<Localized lang="cn">dirt, earth or ground (chinese)</Localized>
				<Localized lang="de">Erde</Localized>
            	<Localized lang="en">dirt, earth or ground</Localized>
				<Localized lang="es">dirt, earth or ground (spanish)</Localized>
            	<Localized lang="fr">dirt, earth or ground (frensh)</Localized>
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
          <Name>gravel</Name>
            <Title>
              gravel
              	<Localized lang="al">gravel (albanian)</Localized>
				<Localized lang="ar">gravel (arabian)</Localized>
            	<Localized lang="cn">gravel (chinese)</Localized>
				<Localized lang="de">Kies</Localized>
            	<Localized lang="en">gravel</Localized>
				<Localized lang="es">gravel (spanish)</Localized>
            	<Localized lang="fr">gravel (frensh)</Localized>
          	</Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:Or>
              <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>surface</ogc:PropertyName>
                <ogc:Literal>fine_gravel</ogc:Literal>
              </ogc:PropertyIsEqualTo>
              <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>surface</ogc:PropertyName>
                <ogc:Literal>gravel</ogc:Literal>
              </ogc:PropertyIsEqualTo>
            </ogc:Or>
          </ogc:Filter>
          <LineSymbolizer>
            <Stroke>
              <CssParameter name="stroke">#bf0ade</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
              <CssParameter name="stroke-linecap">square</CssParameter>
            </Stroke>
          </LineSymbolizer>
        </Rule>
        <Rule>
          <Name>grass or grass paver</Name>
            <Title>
              grass or grass paver
                <Localized lang="al">grass or grass paver(albanian)</Localized>
				<Localized lang="ar">grass or grass paver (arabian)</Localized>
            	<Localized lang="cn">grass or grass paver (chinese)</Localized>
				<Localized lang="de">Grass oder Rasengitterstein</Localized>
            	<Localized lang="en">grass or grass paver</Localized>
				<Localized lang="es">grass or grass paver (spanish)</Localized>
            	<Localized lang="fr">grass or grass paver (frensh)</Localized>
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
          <Name>mud</Name>
            <Title>
              mud
                <Localized lang="al">mud (albanian)</Localized>
				<Localized lang="ar">mud (arabian)</Localized>
            	<Localized lang="cn">mud (chinese)</Localized>
				<Localized lang="de">Schlamm</Localized>
            	<Localized lang="en">mud</Localized>
				<Localized lang="es">mud (spanish)</Localized>
            	<Localized lang="fr">mud (frensh)</Localized>
          	</Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>surface</ogc:PropertyName>
              <ogc:Literal>mud</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <LineSymbolizer>
            <Stroke>
              <CssParameter name="stroke">#f66200</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
              <CssParameter name="stroke-linecap">square</CssParameter>
            </Stroke>
          </LineSymbolizer>
        </Rule>
        <Rule>
          <Name>paved</Name>
            <Title>
              paved
                <Localized lang="al">paved (albanian)</Localized>
				<Localized lang="ar">paved (arabian)</Localized>
            	<Localized lang="cn">paved (chinese)</Localized>
				<Localized lang="de">Befestigte Oberfläche</Localized>
            	<Localized lang="en">paved</Localized>
				<Localized lang="es">paved (spanish)</Localized>
            	<Localized lang="fr">paved (frensh)</Localized>
          	</Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>surface</ogc:PropertyName>
              <ogc:Literal>paved</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <LineSymbolizer>
            <Stroke>
              <CssParameter name="stroke">#3d87a6</CssParameter>
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
        <Rule>
          <Name>pebblestone</Name>
            <Title>
              pebblestone
                <Localized lang="al">pebblestone (albanian)</Localized>
				<Localized lang="ar">pebblestone (arabian)</Localized>
            	<Localized lang="cn">pebblestone (chinese)</Localized>
				<Localized lang="de">Kieselsteine</Localized>
            	<Localized lang="en">pebblestone</Localized>
				<Localized lang="es">pebblestone (spanish)</Localized>
            	<Localized lang="fr">pebblestone (frensh)</Localized>
          	</Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>surface</ogc:PropertyName>
              <ogc:Literal>pebblestone</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <LineSymbolizer>
            <Stroke>
              <CssParameter name="stroke">#ba766d</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
              <CssParameter name="stroke-linecap">square</CssParameter>
            </Stroke>
          </LineSymbolizer>
        </Rule>
        <Rule>
          <Name>sand</Name>
            <Title>
              sand
                <Localized lang="al">sand (albanian)</Localized>
				<Localized lang="ar">sand (arabian)</Localized>
            	<Localized lang="cn">sand (chinese)</Localized>
				<Localized lang="de">Sand</Localized>
            	<Localized lang="en">sand</Localized>
				<Localized lang="es">sand (spanish)</Localized>
            	<Localized lang="fr">sand (frensh)</Localized>
          	</Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>surface</ogc:PropertyName>
              <ogc:Literal>sand</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <LineSymbolizer>
            <Stroke>
              <CssParameter name="stroke">#fdef6f</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
              <CssParameter name="stroke-linecap">square</CssParameter>
            </Stroke>
          </LineSymbolizer>
        </Rule>
        <Rule>
          <Name>stone</Name>
            <Title>
              stone
                <Localized lang="al">stone (albanian)</Localized>
				<Localized lang="ar">stone (arabian)</Localized>
            	<Localized lang="cn">stone (chinese)</Localized>
				<Localized lang="de">Stein</Localized>
            	<Localized lang="en">stone</Localized>
				<Localized lang="es">stone (spanish)</Localized>
            	<Localized lang="fr">stone (frensh)</Localized>
          	</Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>surface</ogc:PropertyName>
              <ogc:Literal>stone</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <LineSymbolizer>
            <Stroke>
              <CssParameter name="stroke">#83bce8</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
              <CssParameter name="stroke-linecap">square</CssParameter>
            </Stroke>
          </LineSymbolizer>
        </Rule>
        <Rule>
          <Name>unpaved</Name>
            <Title>
              unpaved
                <Localized lang="al">unpaved (albanian)</Localized>
				<Localized lang="ar">unpaved (arabian)</Localized>
            	<Localized lang="cn">unpaved (chinese)</Localized>
				<Localized lang="de">unbefestigte Oberfläche</Localized>
            	<Localized lang="en">unpaved</Localized>
				<Localized lang="es">unpaved (spanish)</Localized>
            	<Localized lang="fr">unpaved (frensh)</Localized>
          	</Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>surface</ogc:PropertyName>
              <ogc:Literal>unpaved</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <LineSymbolizer>
            <Stroke>
              <CssParameter name="stroke">#b97e4d</CssParameter>
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