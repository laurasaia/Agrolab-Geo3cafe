<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" xmlns:gml="http://www.opengis.net/gml" version="1.0.0" xmlns:sld="http://www.opengis.net/sld">
  <UserLayer>
    <sld:LayerFeatureConstraints>
      <sld:FeatureTypeConstraint/>
    </sld:LayerFeatureConstraints>
    <sld:UserStyle>
      <sld:Name>Altitude</sld:Name>
      <sld:FeatureTypeStyle>
        <sld:Rule>
          <sld:RasterSymbolizer>
            <sld:ChannelSelection>
              <sld:GrayChannel>
                <sld:SourceChannelName>1</sld:SourceChannelName>
              </sld:GrayChannel>
            </sld:ChannelSelection>
            <sld:ColorMap type="values">
              <sld:ColorMapEntry color="#336600" quantity="1" label="750 - 850 m"/>
              <sld:ColorMapEntry color="#cde787" quantity="2" label="850 - 950 m"/>
              <sld:ColorMapEntry color="#f8d77b" quantity="3" label="950 - 1050 m"/>
              <sld:ColorMapEntry color="#c27523" quantity="4" label="1050 - 1150 m"/>
              <sld:ColorMapEntry color="#714e2b" quantity="5" label="1150 - 1250 m"/>
              <sld:ColorMapEntry color="#d7d7d7" quantity="6" label="1250 - 1350 m"/>
            </sld:ColorMap>
          </sld:RasterSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </UserLayer>
</StyledLayerDescriptor>