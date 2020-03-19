<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:ogc="http://www.opengis.net/ogc" xmlns="http://www.opengis.net/sld" xsi:schemaLocation="http://www.opengis.net/sld StyledLayerDescriptor.xsd" version="1.0.0">
  <NamedLayer>
    <Name>parking</Name>
    <UserStyle>
      <Name>parking</Name>
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
          <Name>diagonal</Name>
            <Title>
              diagonal
                <Localized lang="al">diagonal (albanian)</Localized>
				<Localized lang="ar">diagonal (arabian)</Localized>
            	<Localized lang="cn">diagonal (chinese)</Localized>
				<Localized lang="de">diagonal zur Straße</Localized>
            	<Localized lang="en">diagonal</Localized>
				<Localized lang="es">diagonal (spanish)</Localized>
            	<Localized lang="fr">diagonal (frensh)</Localized>
          	</Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>parking_lane</ogc:PropertyName>
              <ogc:Literal>diagonal</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <LineSymbolizer>
            <Stroke>
              <CssParameter name="stroke">#00c1ce</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
              <CssParameter name="stroke-linecap">square</CssParameter>
            </Stroke>
          </LineSymbolizer>
        </Rule>
        <Rule>
          <Name>perpendicular</Name>
            <Title>
              perpendicular
                <Localized lang="al">perpendicular (albanian)</Localized>
				<Localized lang="ar">perpendicular (arabian)</Localized>
            	<Localized lang="cn">perpendicular (chinese)</Localized>
				<Localized lang="de">senkrecht zur Straße</Localized>
            	<Localized lang="en">perpendicular</Localized>
				<Localized lang="es">perpendicular (spanish)</Localized>
            	<Localized lang="fr">perpendicular (french)</Localized>
          	</Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>parking_lane</ogc:PropertyName>
              <ogc:Literal>perpendicular</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <LineSymbolizer>
            <Stroke>
              <CssParameter name="stroke">#009224</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
              <CssParameter name="stroke-linecap">square</CssParameter>
            </Stroke>
          </LineSymbolizer>
        </Rule>
        <Rule>
          <Name>parallel</Name>
            <Title>
              parallel
                <Localized lang="al">parallel (albanian)</Localized>
				<Localized lang="ar">parallel (arabian)</Localized>
            	<Localized lang="cn">parallel (chinese)</Localized>
				<Localized lang="de">parallel zur Straße</Localized>
            	<Localized lang="en">parallel</Localized>
				<Localized lang="es">parallel (spanish)</Localized>
            	<Localized lang="fr">parallel (french)</Localized>
          	</Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>parking_lane</ogc:PropertyName>
              <ogc:Literal>parallel</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <LineSymbolizer>
            <Stroke>
              <CssParameter name="stroke">#4fd234</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
              <CssParameter name="stroke-linecap">square</CssParameter>
            </Stroke>
          </LineSymbolizer>
        </Rule>
        <Rule>
          <Name>marked</Name>
            <Title>
              marked
                <Localized lang="al">marked (albanian)</Localized>
				<Localized lang="ar">marked (arabian)</Localized>
            	<Localized lang="cn">marked (chinese)</Localized>
				<Localized lang="de">nur in markierten Bereichen</Localized>
            	<Localized lang="en">marked</Localized>
				<Localized lang="es">marked (spanish)</Localized>
            	<Localized lang="fr">marked (french)</Localized>
          	</Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>parking_lane</ogc:PropertyName>
              <ogc:Literal>marked</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <LineSymbolizer>
            <Stroke>
              <CssParameter name="stroke">#f3ff0a</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
              <CssParameter name="stroke-linecap">square</CssParameter>
            </Stroke>
          </LineSymbolizer>
        </Rule>
        <Rule>
          <Name>no_parking</Name>
            <Title>
              no_parking
                <Localized lang="al">no parking (albanian)</Localized>
				<Localized lang="ar">no parking (arabian)</Localized>
            	<Localized lang="cn">no parking (chinese)</Localized>
				<Localized lang="de">Parkverbot</Localized>
            	<Localized lang="en">no parking</Localized>
				<Localized lang="es">no parking (spanish)</Localized>
            	<Localized lang="fr">no parking (french)</Localized>
          	</Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:Or>
              <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>parking_lane</ogc:PropertyName>
                <ogc:Literal>no_parking</ogc:Literal>
              </ogc:PropertyIsEqualTo>
              <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>parking_lane</ogc:PropertyName>
                <ogc:Literal>no</ogc:Literal>
              </ogc:PropertyIsEqualTo>
            </ogc:Or>
          </ogc:Filter>
          <LineSymbolizer>
            <Stroke>
              <CssParameter name="stroke">#ed605b</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
              <CssParameter name="stroke-linecap">square</CssParameter>
            </Stroke>
          </LineSymbolizer>
        </Rule>
        <Rule>
          <Name>no_stopping</Name>
            <Title>
              no_stopping
                <Localized lang="al">no stopping (albanian)</Localized>
				<Localized lang="ar">no stopping (arabian)</Localized>
            	<Localized lang="cn">no stopping (chinese)</Localized>
				<Localized lang="de">Halteverbot</Localized>
            	<Localized lang="en">no stopping</Localized>
				<Localized lang="es">no stopping (spanish)</Localized>
            	<Localized lang="fr">no stopping (french)</Localized>
          	</Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>parking_lane</ogc:PropertyName>
              <ogc:Literal>no_stopping</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <LineSymbolizer>
            <Stroke>
              <CssParameter name="stroke">#ff0901</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
              <CssParameter name="stroke-linecap">square</CssParameter>
            </Stroke>
          </LineSymbolizer>
        </Rule>
        <Rule>
          <Name>fire_lane</Name>
            <Title>
              fire_lane
                <Localized lang="al">fire lane (albanian)</Localized>
				<Localized lang="ar">fire lane (arabian)</Localized>
            	<Localized lang="cn">fire lane (chinese)</Localized>
				<Localized lang="de">Feuerwehrzufahrt</Localized>
            	<Localized lang="en">fire lane</Localized>
				<Localized lang="es">fire lane (spanish)</Localized>
            	<Localized lang="fr">fire lane (french)</Localized>
          	</Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>parking_lane</ogc:PropertyName>
              <ogc:Literal>fire_lane</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <LineSymbolizer>
            <Stroke>
              <CssParameter name="stroke">#d901ff</CssParameter>
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