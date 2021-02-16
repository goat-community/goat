<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:ogc="http://www.opengis.net/ogc" xmlns="http://www.opengis.net/sld" xsi:schemaLocation="http://www.opengis.net/sld StyledLayerDescriptor.xsd" version="1.0.0">
  <NamedLayer>
    <Name>atkis_landuse</Name>
    <UserStyle>
      <Name>atkis_landuse</Name>
      <FeatureTypeStyle>
       <Rule>
          <Name>AX_SportFreizeitUndErholungsflaeche</Name>
            <Title>
              AX_SportFreizeitUndErholungsflaeche
                <Localized lang="de">Sport, Freizeit und Erholungsfläche</Localized>
            	<Localized lang="en">Sports, leisure and recreation area</Localized>
          </Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>landuse</ogc:PropertyName>
              <ogc:Literal>AX_SportFreizeitUndErholungsflaeche</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#32932b</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#232323</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <Name>AX_Friedhof</Name>
            <Title>
              AX_Friedhof
                <Localized lang="de">Friedhof</Localized>
            	<Localized lang="en">Cementery</Localized>
          </Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>landuse</ogc:PropertyName>
              <ogc:Literal>AX_Friedhof</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#e2ce30</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#232323</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <Name>AX_Wohnbauflaeche</Name>
            <Title>
              AX_Wohnbauflaeche
                <Localized lang="de">Wohnbaufläche</Localized>
            	<Localized lang="en">Residential area</Localized>
          </Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>landuse</ogc:PropertyName>
              <ogc:Literal>AX_Wohnbauflaeche</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#e9a029</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#232323</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <Name>AX_FlaecheGemischterNutzung</Name>
            <Title>
              AX_FlaecheGemischterNutzung
              	<Localized lang="de">Fläche gemischter Nutzung</Localized>
            	<Localized lang="en">Area of mixed use</Localized>
          </Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>landuse</ogc:PropertyName>
              <ogc:Literal>AX_FlaecheGemischterNutzung</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#b4381f</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#232323</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <Name>AX_FlaecheBesondererFunktionalerPraegung</Name>
            <Title>
              AX_FlaecheBesondererFunktionalerPraegung
				<Localized lang="de">Fläche besonderer funktionaler Prägung</Localized>
            	<Localized lang="en">Area of special functional characteristics</Localized>
            </Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>landuse</ogc:PropertyName>
              <ogc:Literal>AX_FlaecheBesondererFunktionalerPraegung</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#4881c2</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#232323</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <Name>AX_IndustrieUndGewerbeflaeche</Name>
            <Title>
              AX_IndustrieUndGewerbeflaeche
                <Localized lang="de">Industrie- und Gewerbefläche</Localized>
            	<Localized lang="en">Industrial and commercial area</Localized>
          </Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:Or>
              <ogc:Or>
                <ogc:PropertyIsEqualTo>
                  <ogc:PropertyName>landuse</ogc:PropertyName>
                  <ogc:Literal>AX_IndustrieUndGewerbeflaeche</ogc:Literal>
                </ogc:PropertyIsEqualTo>
                <ogc:PropertyIsEqualTo>
                  <ogc:PropertyName>landuse</ogc:PropertyName>
                  <ogc:Literal>AX_Halde</ogc:Literal>
                </ogc:PropertyIsEqualTo>
              </ogc:Or>
              <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>landuse</ogc:PropertyName>
                <ogc:Literal>AX_TagebauGrubeSteinbruch</ogc:Literal>
              </ogc:PropertyIsEqualTo>
            </ogc:Or>
          </ogc:Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#b6b6b6</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#232323</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <Name>AX_Landwirtschaft</Name>
            <Title>
              AX_Landwirtschaft
                <Localized lang="de">Landwirtschaft</Localized>
            	<Localized lang="en">Agriculture</Localized>
          </Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>landuse</ogc:PropertyName>
              <ogc:Literal>AX_Landwirtschaft</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#c1ce44</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#232323</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <Name>AX_Wald</Name>
            <Title>
              AX_Wald
                <Localized lang="de">Wald</Localized>
            	<Localized lang="en">Forest</Localized>
          </Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>landuse</ogc:PropertyName>
              <ogc:Literal>AX_Wald</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#146614</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#232323</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <Name>AX_Gewaesser</Name>
            <Title>
              AX_Gewaesser
                <Localized lang="de">Gewässer</Localized>
            	<Localized lang="en">Waters</Localized>
          </Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:Or>
              <ogc:Or>
                <ogc:PropertyIsEqualTo>
                  <ogc:PropertyName>landuse</ogc:PropertyName>
                  <ogc:Literal>AX_Fließgewaesser</ogc:Literal>
                </ogc:PropertyIsEqualTo>
                <ogc:PropertyIsEqualTo>
                  <ogc:PropertyName>landuse</ogc:PropertyName>
                  <ogc:Literal>AX_Hafenbecken</ogc:Literal>
                </ogc:PropertyIsEqualTo>
              </ogc:Or>
              <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>landuse</ogc:PropertyName>
                <ogc:Literal>AX_StehendesGewaesser</ogc:Literal>
              </ogc:PropertyIsEqualTo>
            </ogc:Or>
          </ogc:Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#4fa7e1</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#232323</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <Name>AX_Natur</Name>
            <Title>
              AX_Natur
                <Localized lang="de">Natur</Localized>
            	<Localized lang="en">Nature</Localized>
          </Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:Or>
              <ogc:Or>
                <ogc:Or>
                  <ogc:Or>
                <ogc:PropertyIsEqualTo>
                  <ogc:PropertyName>landuse</ogc:PropertyName>
                  <ogc:Literal>AX_Gehoelz</ogc:Literal>
                </ogc:PropertyIsEqualTo>
                <ogc:PropertyIsEqualTo>
                  <ogc:PropertyName>landuse</ogc:PropertyName>
                  <ogc:Literal>AX_Heide</ogc:Literal>
                </ogc:PropertyIsEqualTo>
              </ogc:Or>
              <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>landuse</ogc:PropertyName>
                <ogc:Literal>AX_Moor</ogc:Literal>
              </ogc:PropertyIsEqualTo>
            </ogc:Or>
              <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>landuse</ogc:PropertyName>
                <ogc:Literal>AX_Sumpf</ogc:Literal>
              </ogc:PropertyIsEqualTo>
            </ogc:Or>
              <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>landuse</ogc:PropertyName>
                <ogc:Literal>AX_UnlandVegetationsloseFlaeche</ogc:Literal>
              </ogc:PropertyIsEqualTo>
            </ogc:Or>
          </ogc:Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#8dc05c</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#232323</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <Name>AX_Verkehrsflaechen</Name>
            <Title>
              AX_Verkehrsflaechen
                <Localized lang="de">Verkehrsflächen</Localized>
            	<Localized lang="en">Traffic areas</Localized>
          </Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:Or>
              <ogc:Or>
                <ogc:Or>
                <ogc:PropertyIsEqualTo>
                  <ogc:PropertyName>landuse</ogc:PropertyName>
                  <ogc:Literal>AX_Bahnverkehr</ogc:Literal>
                </ogc:PropertyIsEqualTo>
                <ogc:PropertyIsEqualTo>
                  <ogc:PropertyName>landuse</ogc:PropertyName>
                  <ogc:Literal>AX_Platz</ogc:Literal>
                </ogc:PropertyIsEqualTo>
              </ogc:Or>
              <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>landuse</ogc:PropertyName>
                <ogc:Literal>AX_Strassenverkehr</ogc:Literal>
              </ogc:PropertyIsEqualTo>
            </ogc:Or>
              <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>landuse</ogc:PropertyName>
                <ogc:Literal>AX_Flugverkehr</ogc:Literal>
              </ogc:PropertyIsEqualTo>
            </ogc:Or>
          </ogc:Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#707070</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#232323</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
      </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>