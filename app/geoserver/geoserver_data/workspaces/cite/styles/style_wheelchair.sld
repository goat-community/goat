<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:ogc="http://www.opengis.net/ogc" xmlns="http://www.opengis.net/sld" xsi:schemaLocation="http://www.opengis.net/sld StyledLayerDescriptor.xsd" version="1.0.0">
  <NamedLayer>
    <Name>Wheelchair</Name>
    <UserStyle>
      <Name>Wheelchair</Name>
      <FeatureTypeStyle>
        <Rule>
          <Name>yes</Name>
            <Title>
              yes
            	<Localized lang="al">yes (albanian)</Localized>
				<Localized lang="ar">yes (arabian)</Localized>
           		<Localized lang="cn">yes (chinese)</Localized>
				<Localized lang="de">barrierefrei</Localized>
            	<Localized lang="en">yes </Localized>
				<Localized lang="es">sí</Localized>
            	<Localized lang="fr">oui</Localized>
          </Title>
          	<ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>wheelchair_classified</ogc:PropertyName>
              <ogc:Literal>yes</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <LineSymbolizer>
            <Stroke>
              <CssParameter name="stroke">#13bc54</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
              <CssParameter name="stroke-linecap">square</CssParameter>
            </Stroke>
          </LineSymbolizer>
        </Rule>
        <Rule>
          <Name>limited</Name>
            <Title>
              limited
            	<Localized lang="al">limited (albanian)</Localized>
				<Localized lang="ar">limited (arabian)</Localized>
            	<Localized lang="cn">limited (chinese)</Localized>
				<Localized lang="de">eingeschränkt barrierefrei</Localized>
            	<Localized lang="en">limited</Localized>
				<Localized lang="es">limitado</Localized>
            	<Localized lang="fr">limité</Localized>
          </Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>wheelchair_classified</ogc:PropertyName>
              <ogc:Literal>limited</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <LineSymbolizer>
            <Stroke>
              <CssParameter name="stroke">#ff9807</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
              <CssParameter name="stroke-linecap">square</CssParameter>
            </Stroke>
          </LineSymbolizer>
        </Rule>
        <Rule>
          <Name>no</Name>
            <Title>
              no
                <Localized lang="al">no (albanian)</Localized>
				<Localized lang="ar">no (arabian)</Localized>
           		<Localized lang="cn">no (chinese)</Localized>
				<Localized lang="de">nicht barrierefrei</Localized>
            	<Localized lang="en">no</Localized>
				<Localized lang="es">no</Localized>
            	<Localized lang="fr">non</Localized>
          	</Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>wheelchair_classified</ogc:PropertyName>
              <ogc:Literal>no</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <LineSymbolizer>
            <Stroke>
              <CssParameter name="stroke">#ff1a01</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
              <CssParameter name="stroke-linecap">square</CssParameter>
            </Stroke>
          </LineSymbolizer>
        </Rule>
        <Rule>
          <Name>unclassified</Name>
          <Title>
			unclassified
			<Localized lang="al">unclassified (albanian)</Localized>
			<Localized lang="ar">unclassified (arabian)</Localized>
            <Localized lang="cn">unclassified (chinese)</Localized>
			<Localized lang="de">keine Daten</Localized>
            <Localized lang="en">no data</Localized>
			<Localized lang="es">ningún datos</Localized>
            <Localized lang="fr">pas de données</Localized>
          </Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>wheelchair_classified</ogc:PropertyName>
              <ogc:Literal>unclassified</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <LineSymbolizer>
            <Stroke>
              <CssParameter name="stroke">#99a29d</CssParameter>
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