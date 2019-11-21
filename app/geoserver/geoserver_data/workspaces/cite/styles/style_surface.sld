<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:se="http://www.opengis.net/se" xmlns:ogc="http://www.opengis.net/ogc" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1.1.0" xsi:schemaLocation="http://www.opengis.net/sld http://schemas.opengis.net/sld/1.1.0/StyledLayerDescriptor.xsd">
  <NamedLayer>
    <se:Name>surface</se:Name>
    <UserStyle>
      <se:Name>surface</se:Name>
      <se:FeatureTypeStyle>
        <se:Rule>
          <se:Name>no data</se:Name>
          <se:Description>
            <se:Title>no data</se:Title>
          </se:Description>
          <!--Parser Error: syntax error, unexpected ELSE - Expression was: ELSE-->
          <se:LineSymbolizer>
            <se:Stroke>
              <se:SvgParameter name="stroke">#999999</se:SvgParameter>
              <se:SvgParameter name="stroke-width">1</se:SvgParameter>
              <se:SvgParameter name="stroke-linejoin">bevel</se:SvgParameter>
              <se:SvgParameter name="stroke-linecap">square</se:SvgParameter>
            </se:Stroke>
          </se:LineSymbolizer>
        </se:Rule>
        <se:Rule>
          <se:Name>asphalt</se:Name>
          <se:Description>
            <se:Title>asphalt</se:Title>
          </se:Description>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>surface</ogc:PropertyName>
              <ogc:Literal>asphalt</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <se:LineSymbolizer>
            <se:Stroke>
              <se:SvgParameter name="stroke">#000000</se:SvgParameter>
              <se:SvgParameter name="stroke-width">1</se:SvgParameter>
              <se:SvgParameter name="stroke-linejoin">bevel</se:SvgParameter>
              <se:SvgParameter name="stroke-linecap">square</se:SvgParameter>
            </se:Stroke>
          </se:LineSymbolizer>
        </se:Rule>
        <se:Rule>
          <se:Name>broken</se:Name>
          <se:Description>
            <se:Title>broken</se:Title>
          </se:Description>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>surface</ogc:PropertyName>
              <ogc:Literal>broken</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <se:LineSymbolizer>
            <se:Stroke>
              <se:SvgParameter name="stroke">#eb3e47</se:SvgParameter>
              <se:SvgParameter name="stroke-width">1</se:SvgParameter>
              <se:SvgParameter name="stroke-linejoin">bevel</se:SvgParameter>
              <se:SvgParameter name="stroke-linecap">square</se:SvgParameter>
            </se:Stroke>
          </se:LineSymbolizer>
        </se:Rule>
        <se:Rule>
          <se:Name>cobblestone</se:Name>
          <se:Description>
            <se:Title>cobblestone</se:Title>
          </se:Description>
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
          <se:LineSymbolizer>
            <se:Stroke>
              <se:SvgParameter name="stroke">#696969</se:SvgParameter>
              <se:SvgParameter name="stroke-width">1</se:SvgParameter>
              <se:SvgParameter name="stroke-linejoin">bevel</se:SvgParameter>
              <se:SvgParameter name="stroke-linecap">square</se:SvgParameter>
            </se:Stroke>
          </se:LineSymbolizer>
        </se:Rule>
        <se:Rule>
          <se:Name>compacted</se:Name>
          <se:Description>
            <se:Title>compacted</se:Title>
          </se:Description>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>surface</ogc:PropertyName>
              <ogc:Literal>compacted</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <se:LineSymbolizer>
            <se:Stroke>
              <se:SvgParameter name="stroke">#ea9185</se:SvgParameter>
              <se:SvgParameter name="stroke-width">1</se:SvgParameter>
              <se:SvgParameter name="stroke-linejoin">bevel</se:SvgParameter>
              <se:SvgParameter name="stroke-linecap">square</se:SvgParameter>
            </se:Stroke>
          </se:LineSymbolizer>
        </se:Rule>
        <se:Rule>
          <se:Name>concrete</se:Name>
          <se:Description>
            <se:Title>concrete</se:Title>
          </se:Description>
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
          <se:LineSymbolizer>
            <se:Stroke>
              <se:SvgParameter name="stroke">#266bca</se:SvgParameter>
              <se:SvgParameter name="stroke-width">1</se:SvgParameter>
              <se:SvgParameter name="stroke-linejoin">bevel</se:SvgParameter>
              <se:SvgParameter name="stroke-linecap">square</se:SvgParameter>
            </se:Stroke>
          </se:LineSymbolizer>
        </se:Rule>
        <se:Rule>
          <se:Name>dirt, earth or ground</se:Name>
          <se:Description>
            <se:Title>dirt, earth or ground</se:Title>
          </se:Description>
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
          <se:LineSymbolizer>
            <se:Stroke>
              <se:SvgParameter name="stroke">#ad7940</se:SvgParameter>
              <se:SvgParameter name="stroke-width">1</se:SvgParameter>
              <se:SvgParameter name="stroke-linejoin">bevel</se:SvgParameter>
              <se:SvgParameter name="stroke-linecap">square</se:SvgParameter>
            </se:Stroke>
          </se:LineSymbolizer>
        </se:Rule>
        <se:Rule>
          <se:Name>gravel</se:Name>
          <se:Description>
            <se:Title>gravel</se:Title>
          </se:Description>
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
          <se:LineSymbolizer>
            <se:Stroke>
              <se:SvgParameter name="stroke">#bf0ade</se:SvgParameter>
              <se:SvgParameter name="stroke-width">1</se:SvgParameter>
              <se:SvgParameter name="stroke-linejoin">bevel</se:SvgParameter>
              <se:SvgParameter name="stroke-linecap">square</se:SvgParameter>
            </se:Stroke>
          </se:LineSymbolizer>
        </se:Rule>
        <se:Rule>
          <se:Name>grass or grass paver</se:Name>
          <se:Description>
            <se:Title>grass or grass paver</se:Title>
          </se:Description>
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
          <se:LineSymbolizer>
            <se:Stroke>
              <se:SvgParameter name="stroke">#0cae3f</se:SvgParameter>
              <se:SvgParameter name="stroke-width">1</se:SvgParameter>
              <se:SvgParameter name="stroke-linejoin">bevel</se:SvgParameter>
              <se:SvgParameter name="stroke-linecap">square</se:SvgParameter>
            </se:Stroke>
          </se:LineSymbolizer>
        </se:Rule>
        <se:Rule>
          <se:Name>mud</se:Name>
          <se:Description>
            <se:Title>mud</se:Title>
          </se:Description>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>surface</ogc:PropertyName>
              <ogc:Literal>mud</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <se:LineSymbolizer>
            <se:Stroke>
              <se:SvgParameter name="stroke">#f66200</se:SvgParameter>
              <se:SvgParameter name="stroke-width">1</se:SvgParameter>
              <se:SvgParameter name="stroke-linejoin">bevel</se:SvgParameter>
              <se:SvgParameter name="stroke-linecap">square</se:SvgParameter>
            </se:Stroke>
          </se:LineSymbolizer>
        </se:Rule>
        <se:Rule>
          <se:Name>paved</se:Name>
          <se:Description>
            <se:Title>paved</se:Title>
          </se:Description>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>surface</ogc:PropertyName>
              <ogc:Literal>paved</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <se:LineSymbolizer>
            <se:Stroke>
              <se:SvgParameter name="stroke">#3d87a6</se:SvgParameter>
              <se:SvgParameter name="stroke-width">1</se:SvgParameter>
              <se:SvgParameter name="stroke-linejoin">bevel</se:SvgParameter>
              <se:SvgParameter name="stroke-linecap">square</se:SvgParameter>
            </se:Stroke>
          </se:LineSymbolizer>
        </se:Rule>
        <se:Rule>
          <se:Name>paving stones</se:Name>
          <se:Description>
            <se:Title>paving stones</se:Title>
          </se:Description>
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
          <se:LineSymbolizer>
            <se:Stroke>
              <se:SvgParameter name="stroke">#32c9ea</se:SvgParameter>
              <se:SvgParameter name="stroke-width">1</se:SvgParameter>
              <se:SvgParameter name="stroke-linejoin">bevel</se:SvgParameter>
              <se:SvgParameter name="stroke-linecap">square</se:SvgParameter>
            </se:Stroke>
          </se:LineSymbolizer>
        </se:Rule>
        <se:Rule>
          <se:Name>pebblestone</se:Name>
          <se:Description>
            <se:Title>pebblestone</se:Title>
          </se:Description>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>surface</ogc:PropertyName>
              <ogc:Literal>pebblestone</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <se:LineSymbolizer>
            <se:Stroke>
              <se:SvgParameter name="stroke">#ba766d</se:SvgParameter>
              <se:SvgParameter name="stroke-width">1</se:SvgParameter>
              <se:SvgParameter name="stroke-linejoin">bevel</se:SvgParameter>
              <se:SvgParameter name="stroke-linecap">square</se:SvgParameter>
            </se:Stroke>
          </se:LineSymbolizer>
        </se:Rule>
        <se:Rule>
          <se:Name>sand</se:Name>
          <se:Description>
            <se:Title>sand</se:Title>
          </se:Description>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>surface</ogc:PropertyName>
              <ogc:Literal>sand</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <se:LineSymbolizer>
            <se:Stroke>
              <se:SvgParameter name="stroke">#fdef6f</se:SvgParameter>
              <se:SvgParameter name="stroke-width">1</se:SvgParameter>
              <se:SvgParameter name="stroke-linejoin">bevel</se:SvgParameter>
              <se:SvgParameter name="stroke-linecap">square</se:SvgParameter>
            </se:Stroke>
          </se:LineSymbolizer>
        </se:Rule>
        <se:Rule>
          <se:Name>stone</se:Name>
          <se:Description>
            <se:Title>stone</se:Title>
          </se:Description>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>surface</ogc:PropertyName>
              <ogc:Literal>stone</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <se:LineSymbolizer>
            <se:Stroke>
              <se:SvgParameter name="stroke">#83bce8</se:SvgParameter>
              <se:SvgParameter name="stroke-width">1</se:SvgParameter>
              <se:SvgParameter name="stroke-linejoin">bevel</se:SvgParameter>
              <se:SvgParameter name="stroke-linecap">square</se:SvgParameter>
            </se:Stroke>
          </se:LineSymbolizer>
        </se:Rule>
        <se:Rule>
          <se:Name>unpaved</se:Name>
          <se:Description>
            <se:Title>unpaved</se:Title>
          </se:Description>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>surface</ogc:PropertyName>
              <ogc:Literal>unpaved</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <se:LineSymbolizer>
            <se:Stroke>
              <se:SvgParameter name="stroke">#b97e4d</se:SvgParameter>
              <se:SvgParameter name="stroke-width">1</se:SvgParameter>
              <se:SvgParameter name="stroke-linejoin">bevel</se:SvgParameter>
              <se:SvgParameter name="stroke-linecap">square</se:SvgParameter>
            </se:Stroke>
          </se:LineSymbolizer>
        </se:Rule>
      </se:FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>