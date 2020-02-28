<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:ogc="http://www.opengis.net/ogc" xmlns="http://www.opengis.net/sld" xsi:schemaLocation="http://www.opengis.net/sld StyledLayerDescriptor.xsd" version="1.0.0">
  <NamedLayer>
    <Name>smoothness</Name>
    <UserStyle>
      <Name>smoothness</Name>
      <FeatureTypeStyle>
        <Rule>
          <Name>no data</Name>
            <Title>
              no data
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
          <Name>impassable</Name>
            <Title>
              impassable
          		<Localized lang="de">nicht befahrbar</Localized>
            	<Localized lang="en">impassable</Localized>
          </Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>smoothness</ogc:PropertyName>
              <ogc:Literal>impassable</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <LineSymbolizer>
            <Stroke>
              <CssParameter name="stroke">#bf1000</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
              <CssParameter name="stroke-linecap">square</CssParameter>
            </Stroke>
          </LineSymbolizer>
        </Rule>
        <Rule>
          <Name>intermediate</Name>
            <Title>
              intermediate
				<Localized lang="de">mittelmäßig</Localized>
            	<Localized lang="en">intermediate</Localized>
          	</Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>smoothness</ogc:PropertyName>
              <ogc:Literal>intermediate</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <LineSymbolizer>
            <Stroke>
              <CssParameter name="stroke">#e3a619</CssParameter>
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