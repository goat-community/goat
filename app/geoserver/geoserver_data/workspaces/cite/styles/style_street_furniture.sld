<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:ogc="http://www.opengis.net/ogc" xmlns="http://www.opengis.net/sld" xsi:schemaLocation="http://www.opengis.net/sld StyledLayerDescriptor.xsd" version="1.0.0">
  <NamedLayer>
    <Name>street_furniture</Name>
    <UserStyle>
      <Name>street_furniture</Name>
      <FeatureTypeStyle>
        <Rule>
          <Name>bench</Name>
            <Title>
              bench
                <Localized lang="al">bench (albanian)</Localized>
				<Localized lang="ar">bench (arabian)</Localized>
            	<Localized lang="cn">bench (chinese)</Localized>
				<Localized lang="de">Parkbank</Localized>
            	<Localized lang="en">bench</Localized>
				<Localized lang="es">banca</Localized>
            	<Localized lang="fr">banc</Localized>
          	</Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>amenity</ogc:PropertyName>
              <ogc:Literal>bench</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <PointSymbolizer>
            <Graphic>
              <Mark>
                <WellKnownName>circle</WellKnownName>
                <Fill>
                  <CssParameter name="fill">#83d739</CssParameter>
                </Fill>
                <Stroke>
                  <CssParameter name="stroke">#232323</CssParameter>
                  <CssParameter name="stroke-width">0.5</CssParameter>
                </Stroke>
              </Mark>
              <Size>7</Size>
            </Graphic>
          </PointSymbolizer>
        </Rule>
        <Rule>
          <Name>toilets</Name>
            <Title>
              toilets
                <Localized lang="al">toilets (albanian)</Localized>
				<Localized lang="ar">toilets (arabian)</Localized>
            	<Localized lang="cn">toilets (chinese)</Localized>
				<Localized lang="de">Öffentliche Toilette</Localized>
            	<Localized lang="en">toilets</Localized>
				<Localized lang="es">servicio público</Localized>
            	<Localized lang="fr">toilet public</Localized>
          	</Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>amenity</ogc:PropertyName>
              <ogc:Literal>toilets</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <PointSymbolizer>
            <Graphic>
              <Mark>
                <WellKnownName>circle</WellKnownName>
                <Fill>
                  <CssParameter name="fill">#ffd000</CssParameter>
                </Fill>
                <Stroke>
                  <CssParameter name="stroke">#232323</CssParameter>
                  <CssParameter name="stroke-width">0.5</CssParameter>
                </Stroke>
              </Mark>
              <Size>7</Size>
            </Graphic>
          </PointSymbolizer>
        </Rule>
       <Rule>
          <Name>fountain</Name>
            <Title>
              fountain
                <Localized lang="al">fountain (albanian)</Localized>
				<Localized lang="ar">fountain (arabian)</Localized>
            	<Localized lang="cn">fountain (chinese)</Localized>
				<Localized lang="de">Springbrunnen</Localized>
            	<Localized lang="en">fountain</Localized>
				<Localized lang="es">fuente</Localized>
            	<Localized lang="fr">fontaine</Localized>
         	</Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>amenity</ogc:PropertyName>
              <ogc:Literal>fountain</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <PointSymbolizer>
            <Graphic>
              <Mark>
                <WellKnownName>circle</WellKnownName>
                <Fill>
                  <CssParameter name="fill">#30d0e6</CssParameter>
                </Fill>
                <Stroke>
                  <CssParameter name="stroke">#232323</CssParameter>
                  <CssParameter name="stroke-width">0.5</CssParameter>
                </Stroke>
              </Mark>
              <Size>7</Size>
            </Graphic>
          </PointSymbolizer>
        </Rule>
        <Rule>
          <Name>waste_basket</Name>
            <Title>
              waste_basket
                <Localized lang="al">waste basket (albanian)</Localized>
				<Localized lang="ar">waste basket (arabian)</Localized>
            	<Localized lang="cn">waste basket (chinese)</Localized>
				<Localized lang="de">Mülleimer</Localized>
            	<Localized lang="en">waste basket</Localized>
				<Localized lang="es">cubo de basura</Localized>
            	<Localized lang="fr">poubelle</Localized>
          	</Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>amenity</ogc:PropertyName>
              <ogc:Literal>waste_basket</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <PointSymbolizer>
            <Graphic>
              <Mark>
                <WellKnownName>circle</WellKnownName>
                <Fill>
                  <CssParameter name="fill">#f03f3f</CssParameter>
                </Fill>
                <Stroke>
                  <CssParameter name="stroke">#232323</CssParameter>
                  <CssParameter name="stroke-width">0.5</CssParameter>
                </Stroke>
              </Mark>
              <Size>7</Size>
            </Graphic>
          </PointSymbolizer>
        </Rule>
      </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>