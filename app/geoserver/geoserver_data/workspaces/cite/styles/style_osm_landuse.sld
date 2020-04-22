<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:ogc="http://www.opengis.net/ogc" xmlns="http://www.opengis.net/sld" xsi:schemaLocation="http://www.opengis.net/sld StyledLayerDescriptor.xsd" version="1.0.0">
  <NamedLayer>
    <Name>osm_landuse</Name>
    <UserStyle>
      <Name>osm_landuse</Name>
      <FeatureTypeStyle>
        <Rule>
          <Name>water</Name>
            <Title>
              water
                <Localized lang="de">Gewässer</Localized>
            	<Localized lang="en">Waters</Localized>
          	</Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:Or>
              <ogc:Or>
                <ogc:PropertyIsEqualTo>
                  <ogc:PropertyName>landuse</ogc:PropertyName>
                  <ogc:Literal>basin</ogc:Literal>
                </ogc:PropertyIsEqualTo>
                <ogc:PropertyIsEqualTo>
                  <ogc:PropertyName>landuse</ogc:PropertyName>
                  <ogc:Literal>reservoir</ogc:Literal>
                </ogc:PropertyIsEqualTo>
              </ogc:Or>
              <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>landuse</ogc:PropertyName>
                <ogc:Literal>salt_pond</ogc:Literal>
              </ogc:PropertyIsEqualTo>
                <ogc:PropertyIsEqualTo>
                  <ogc:PropertyName>landuse</ogc:PropertyName>
                  <ogc:Literal>waters</ogc:Literal>
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
          <Name>agriculture</Name>
            <Title>
              agriculture
                <Localized lang="de">Grünflächen und Landwirtschaft</Localized>
            	<Localized lang="en">Green Areas and Agriculture</Localized>
          </Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:Or>
              <ogc:Or>
                <ogc:Or>
                  <ogc:Or>
                    <ogc:Or>
                      <ogc:Or>
                        <ogc:Or>
                          <ogc:Or>
                            <ogc:Or>
                              <ogc:Or>
                                <ogc:Or>
                                  <ogc:Or>
                                    <ogc:Or>
                                      <ogc:PropertyIsEqualTo>
                                        <ogc:PropertyName>landuse</ogc:PropertyName>
                                        <ogc:Literal>allotments</ogc:Literal>
                                      </ogc:PropertyIsEqualTo>
                                      <ogc:PropertyIsEqualTo>
                                        <ogc:PropertyName>landuse</ogc:PropertyName>
                                        <ogc:Literal>aquaculture</ogc:Literal>
                                      </ogc:PropertyIsEqualTo>
                                    </ogc:Or>
                                    <ogc:PropertyIsEqualTo>
                                      <ogc:PropertyName>landuse</ogc:PropertyName>
                                      <ogc:Literal>fallow</ogc:Literal>
                                    </ogc:PropertyIsEqualTo>
                                  </ogc:Or>
                                  <ogc:PropertyIsEqualTo>
                                    <ogc:PropertyName>landuse</ogc:PropertyName>
                                    <ogc:Literal>farmland</ogc:Literal>
                                  </ogc:PropertyIsEqualTo>
                                </ogc:Or>
                                <ogc:PropertyIsEqualTo>
                                  <ogc:PropertyName>landuse</ogc:PropertyName>
                                  <ogc:Literal>farmyard</ogc:Literal>
                                </ogc:PropertyIsEqualTo>
                              </ogc:Or>
                              <ogc:PropertyIsEqualTo>
                                <ogc:PropertyName>landuse</ogc:PropertyName>
                                <ogc:Literal>forest</ogc:Literal>
                              </ogc:PropertyIsEqualTo>
                            </ogc:Or>
                            <ogc:PropertyIsEqualTo>
                              <ogc:PropertyName>landuse</ogc:PropertyName>
                              <ogc:Literal>meadow</ogc:Literal>
                            </ogc:PropertyIsEqualTo>
                          </ogc:Or>
                          <ogc:PropertyIsEqualTo>
                            <ogc:PropertyName>landuse</ogc:PropertyName>
                            <ogc:Literal>greenhouse_horticulture</ogc:Literal>
                          </ogc:PropertyIsEqualTo>
                        </ogc:Or>
                        <ogc:PropertyIsEqualTo>
                          <ogc:PropertyName>landuse</ogc:PropertyName>
                          <ogc:Literal>grass</ogc:Literal>
                        </ogc:PropertyIsEqualTo>
                      </ogc:Or>
                      <ogc:PropertyIsEqualTo>
                        <ogc:PropertyName>landuse</ogc:PropertyName>
                        <ogc:Literal>orchard</ogc:Literal>
                      </ogc:PropertyIsEqualTo>
                    </ogc:Or>
                    <ogc:PropertyIsEqualTo>
                      <ogc:PropertyName>landuse</ogc:PropertyName>
                      <ogc:Literal>pasture</ogc:Literal>
                    </ogc:PropertyIsEqualTo>
                  </ogc:Or>
                  <ogc:PropertyIsEqualTo>
                    <ogc:PropertyName>landuse</ogc:PropertyName>
                    <ogc:Literal>plant_nursery</ogc:Literal>
                  </ogc:PropertyIsEqualTo>
                </ogc:Or>
                <ogc:PropertyIsEqualTo>
                  <ogc:PropertyName>landuse</ogc:PropertyName>
                  <ogc:Literal>plantation</ogc:Literal>
                </ogc:PropertyIsEqualTo>
              </ogc:Or>
              <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>landuse</ogc:PropertyName>
                <ogc:Literal>vineyard</ogc:Literal>
              </ogc:PropertyIsEqualTo>
               <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>landuse</ogc:PropertyName>
                <ogc:Literal>green_area</ogc:Literal>
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
          <Name>leisure</Name>
            <Title>
              leisure
                <Localized lang="de">Sport- und Freizeitflächen</Localized>
            	<Localized lang="en">Sports and leisure areas</Localized>
          	</Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:Or>
              <ogc:Or>
                <ogc:Or>
                  <ogc:Or>
                    <ogc:Or>
                      <ogc:PropertyIsEqualTo>
                        <ogc:PropertyName>landuse</ogc:PropertyName>
                        <ogc:Literal>garden</ogc:Literal>
                      </ogc:PropertyIsEqualTo>
                      <ogc:PropertyIsEqualTo>
                        <ogc:PropertyName>landuse</ogc:PropertyName>
                        <ogc:Literal>national_park</ogc:Literal>
                      </ogc:PropertyIsEqualTo>
                    </ogc:Or>
                    <ogc:PropertyIsEqualTo>
                      <ogc:PropertyName>landuse</ogc:PropertyName>
                      <ogc:Literal>nature_reserve</ogc:Literal>
                    </ogc:PropertyIsEqualTo>
                  </ogc:Or>
                  <ogc:PropertyIsEqualTo>
                    <ogc:PropertyName>landuse</ogc:PropertyName>
                    <ogc:Literal>park</ogc:Literal>
                  </ogc:PropertyIsEqualTo>
                </ogc:Or>
                <ogc:PropertyIsEqualTo>
                  <ogc:PropertyName>landuse</ogc:PropertyName>
                  <ogc:Literal>village_green</ogc:Literal>
                </ogc:PropertyIsEqualTo>
              </ogc:Or>
              <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>landuse</ogc:PropertyName>
                <ogc:Literal>recreation_ground</ogc:Literal>
              </ogc:PropertyIsEqualTo>
               <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>landuse</ogc:PropertyName>
                <ogc:Literal>leisure</ogc:Literal>
              </ogc:PropertyIsEqualTo>
            </ogc:Or>
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
          <Name>cemetery</Name>
            <Title>
              cemetery
                <Localized lang="de">Friedhof</Localized>
            	<Localized lang="en">Cementery</Localized>
         	</Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:Or>
              <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>landuse</ogc:PropertyName>
                <ogc:Literal>cemetery</ogc:Literal>
              </ogc:PropertyIsEqualTo>
              <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>landuse</ogc:PropertyName>
                <ogc:Literal>grave_yard</ogc:Literal>
              </ogc:PropertyIsEqualTo>
            </ogc:Or>
          </ogc:Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#d7e882</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#232323</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <Name>residential</Name>
            <Title>
              residential
                <Localized lang="de">Wohngebiet</Localized>
            	<Localized lang="en">Residential area</Localized>
          	</Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:Or>
              <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>landuse</ogc:PropertyName>
                <ogc:Literal>residential</ogc:Literal>
              </ogc:PropertyIsEqualTo>
              <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>landuse</ogc:PropertyName>
                <ogc:Literal>garages</ogc:Literal>
              </ogc:PropertyIsEqualTo>
            </ogc:Or>
          </ogc:Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#e7993a</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#232323</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <Name>commercial</Name>
            <Title>
              commercial
                <Localized lang="de">Gewerbegebiet</Localized>
            	<Localized lang="en">Commercial area</Localized>
          	</Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:Or>
              <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>landuse</ogc:PropertyName>
                <ogc:Literal>commercial</ogc:Literal>
              </ogc:PropertyIsEqualTo>
              <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>landuse</ogc:PropertyName>
                <ogc:Literal>retail</ogc:Literal>
              </ogc:PropertyIsEqualTo>
            </ogc:Or>
          </ogc:Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#d35153</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#232323</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <Name>community</Name>
            <Title>
              community
                <Localized lang="de">Gemeinschaftseinrichtungen</Localized>
            	<Localized lang="en">Community facilities</Localized>
          	</Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:Or>
              <ogc:Or>
                <ogc:Or>
                  <ogc:Or>
                    <ogc:Or>
                      <ogc:PropertyIsEqualTo>
                        <ogc:PropertyName>landuse</ogc:PropertyName>
                        <ogc:Literal>school</ogc:Literal>
                      </ogc:PropertyIsEqualTo>
                      <ogc:PropertyIsEqualTo>
                        <ogc:PropertyName>landuse</ogc:PropertyName>
                        <ogc:Literal>university</ogc:Literal>
                      </ogc:PropertyIsEqualTo>
                    </ogc:Or>
                    <ogc:PropertyIsEqualTo>
                      <ogc:PropertyName>landuse</ogc:PropertyName>
                      <ogc:Literal>hospital</ogc:Literal>
                    </ogc:PropertyIsEqualTo>
                  </ogc:Or>
                  <ogc:PropertyIsEqualTo>
                    <ogc:PropertyName>landuse</ogc:PropertyName>
                    <ogc:Literal>college</ogc:Literal>
                  </ogc:PropertyIsEqualTo>
                </ogc:Or>
                <ogc:PropertyIsEqualTo>
                  <ogc:PropertyName>landuse</ogc:PropertyName>
                  <ogc:Literal>churchyard</ogc:Literal>
                </ogc:PropertyIsEqualTo>
              </ogc:Or>
              <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>landuse</ogc:PropertyName>
                <ogc:Literal>religious</ogc:Literal>
              </ogc:PropertyIsEqualTo>
              <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>landuse</ogc:PropertyName>
                <ogc:Literal>community</ogc:Literal>
              </ogc:PropertyIsEqualTo>
            </ogc:Or>
          </ogc:Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#4877d5</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#232323</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <Name>industrial</Name>
            <Title>
              industrial
                <Localized lang="de">Industriegebiet</Localized>
            	<Localized lang="en">Industrial area</Localized>
          	</Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:Or>
              <ogc:Or>
                <ogc:PropertyIsEqualTo>
                  <ogc:PropertyName>landuse</ogc:PropertyName>
                  <ogc:Literal>industrial</ogc:Literal>
                </ogc:PropertyIsEqualTo>
                <ogc:PropertyIsEqualTo>
                  <ogc:PropertyName>landuse</ogc:PropertyName>
                  <ogc:Literal>landfill</ogc:Literal>
                </ogc:PropertyIsEqualTo>
              </ogc:Or>
              <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>landuse</ogc:PropertyName>
                <ogc:Literal>quarry</ogc:Literal>
              </ogc:PropertyIsEqualTo>
            </ogc:Or>
          </ogc:Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#aab1b5</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#232323</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <Name>transportation</Name>
            <Title>
              transportation
                <Localized lang="de">Transportflächen</Localized>
            	<Localized lang="en">Transportation</Localized>
          	</Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:Or>
              <ogc:Or>
                <ogc:PropertyIsEqualTo>
                  <ogc:PropertyName>landuse</ogc:PropertyName>
                  <ogc:Literal>highway</ogc:Literal>
                </ogc:PropertyIsEqualTo>
                <ogc:PropertyIsEqualTo>
                  <ogc:PropertyName>landuse</ogc:PropertyName>
                  <ogc:Literal>parking</ogc:Literal>
                </ogc:PropertyIsEqualTo>
              </ogc:Or>
              <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>landuse</ogc:PropertyName>
                <ogc:Literal>railway</ogc:Literal>
              </ogc:PropertyIsEqualTo>
            </ogc:Or>
          </ogc:Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#e1a3b3</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#232323</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <Name>military</Name>
            <Title>
              military
                <Localized lang="de">Militärgebiet</Localized>
            	<Localized lang="en">Military area</Localized>
          	</Title>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>landuse</ogc:PropertyName>
              <ogc:Literal>military</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#8bffc3</CssParameter>
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