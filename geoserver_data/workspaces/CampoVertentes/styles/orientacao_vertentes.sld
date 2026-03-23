<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor xmlns="http://www.opengis.net/sld" version="1.0.0" xmlns:ogc="http://www.opengis.net/ogc" xmlns:sld="http://www.opengis.net/sld" xmlns:gml="http://www.opengis.net/gml">
  <UserLayer>
    <sld:LayerFeatureConstraints>
      <sld:FeatureTypeConstraint/>
    </sld:LayerFeatureConstraints>
    <sld:UserStyle>
      <sld:Name>orientacao-vertentes-recortado</sld:Name>
      <sld:FeatureTypeStyle>
        <sld:Rule>
          <sld:RasterSymbolizer>
            <sld:ChannelSelection>
              <sld:GrayChannel>
                <sld:SourceChannelName>1</sld:SourceChannelName>
              </sld:GrayChannel>
            </sld:ChannelSelection>
            <sld:ColorMap type="intervals">
              <sld:ColorMapEntry color="#ff0000" quantity="45" label="0 - 45&#176; (N)"/>
              <sld:ColorMapEntry color="#ff7b00" quantity="90" label="45 - 90&#176; (NE)"/>
              <sld:ColorMapEntry color="#ffff00" quantity="135" label="90 - 135&#176; (E)"/>
              <sld:ColorMapEntry color="#00c900" quantity="180" label="135 - 180&#176; (SE)"/>
              <sld:ColorMapEntry color="#3fe0ff" quantity="225" label="180 - 225&#176; (S)"/>
              <sld:ColorMapEntry color="#007bd0" quantity="270" label="225 - 270&#176; (SW)"/>
              <sld:ColorMapEntry color="#1013c3" quantity="315" label="270 - 315&#176; (W)"/>
              <sld:ColorMapEntry color="#fa4fff" quantity="360" label="315 - 360&#176; (NW)"/>
            </sld:ColorMap>
          </sld:RasterSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </UserLayer>
</StyledLayerDescriptor>