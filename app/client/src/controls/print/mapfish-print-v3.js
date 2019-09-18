/**
 * @typedef {Object} MapFishPrintCapabilities
 * @property {Object<srring, MapFishPrintCapabilitiesLayout>} layouts
 * @property {string[]} formats
 * @property {MapFishPrintCapabilitiesSMTP} [smtp] STMP object definition
 */

/**
 * Fields that can come from a print v3 server and can be used in the partial
 * of the gmf print panel.
 * @typedef {Object} MapFishPrintCapabilitiesLayout
 * @property {string} name
 * @property {MapFishPrintCapabilitiesLayoutAttribute[]} [attributes] Custom print layoutInfo.
 */

/**
 * @typedef {Object} MapFishPrintCapabilitiesLayoutAttribute
 * @property {string} name Name of the form field.
 * @property {string|boolean|number} [default] Default value of the form field.
 * @property {string} value
 * @property {string} type Type of the field. Can be 'String', 'Boolean' or 'Number'.
 * @property {string} [clientParams]
 */

/**
 * @typedef {Object} MapFishPrintCapabilitiesSMTP
 * @property {boolean} enabled
 */

/**
 * @typedef {Object} DataSourceTableObject
 * @property {string[]} columns
 * @property {Array<Array<string|number|boolean>>} data
 */

/**
 * @typedef {Object} DataSourcePrintReportObject
 * @property {string} title
 * @property {DataSourceTableObject} table
 */

/**
 * @typedef {Object} MapFishPrintSpec
 * @property {MapFishPrintAttributes} attributes
 * @property {string} layout
 * @property {string} format
 * @property {string} lang
 * @property {MapFishPrintSMTP} [smtp] STMP object definition
 */

/**
 * @typedef {Object} MapFishPrintAttributes
 * @property {MapFishPrintMap} map
 */

/**
 * @typedef {Object} MapFishPrintMap
 * @property {number[]} bbox
 * @property {number[]} center
 * @property {number} scale
 * @property {number} dpi
 * @property {MapFishPrintLayer[]} layers
 * @property {string} projection
 * @property {number} rotation
 */

/**
 * @typedef {Object} MapFishPrintLayer
 * @property {string} type
 * @property {number} opacity
 */

/**
 * extends {MapFishPrintLayer}
 * @typedef {Object} MapFishPrintVectorLayer
 * @property {string} type (MapFishPrintLayer)
 * @property {number} opacity (MapFishPrintLayer)
 * @property {import("geojson").Object} geoJson
 * @property {MapFishPrintVectorStyle} style
 */

/**
 * @typedef {Object} MapFishPrintVectorStyle
 * @property {number} version
 */

/**
 * extends {MapFishPrintLayer}
 * @typedef {Object} MapFishPrintWmsLayer
 * @property {string} type (MapFishPrintLayer)
 * @property {number} opacity (MapFishPrintLayer)
 * @property {string} baseURL
 * @property {Object<string, string>} customParams
 * @property {string[]} layers
 * @property {string} serverType
 * @property {string[]} [styles]
 * @property {string} version
 * @property {boolean} useNativeAngle
 * @property {string} imageFormat
 */

/**
 * @typedef {Object} MapFishPrintWmtsMatrix
 * @property {string} identifier
 * @property {number} scaleDenominator
 * @property {number[]} tileSize
 * @property {number[]} topLeftCorner
 * @property {number[]} matrixSize
 */

/**
 * extends {MapFishPrintLayer}
 * @typedef {Object} MapFishPrintWmtsLayer
 * @property {string} type (MapFishPrintLayer)
 * @property {number} opacity (MapFishPrintLayer)
 * @property {string} baseURL
 * @property {Object} dimensions
 * @property {Object} dimensionParams
 * @property {string} imageFormat
 * @property {string} layer
 * @property {MapFishPrintWmtsMatrix[]} matrices
 * @property {string} matrixSet
 * @property {string} requestEncoding
 * @property {string} style
 * @property {string} version
 */

/**
 * @typedef {Object} MapFishPrintReportResponse
 * @property {string} ref
 * @property {string} [statusURL]
 * @property {string} [downloadURL]
 */

/**
 * @typedef {Object} MapFishPrintStatusResponse
 * @property {boolean} done
 * @property {string} [status]
 * @property {string} [error]
 * @property {string} [downloadURL]
 */

/**
 * @typedef {Object} MapFishPrintSymbolizers
 * @property {MapFishPrintSymbolizer[]} symbolizers
 */

/**
 * @typedef {Object} MapFishPrintSymbolizer
 * @property {string} type
 */

/**
 * extends {MapFishPrintSymbolizer}
 * @typedef {Object} MapFishPrintSymbolizerLine
 * @property {string} type (MapFishPrintSymbolizer)
 * @property {string} strokeColor
 * @property {number} strokeOpacity
 * @property {number} strokeWidth
 * @property {string} strokeDashstyle
 * @property {string} strokeLinecap
 */

/**
 * extends {MapFishPrintSymbolizer}
 * @typedef {Object} MapFishPrintSymbolizerPoint
 * @property {string} type (MapFishPrintSymbolizer)
 * @property {string} externalGraphic
 * @property {string} graphicFormat
 * @property {number} graphicOpacity
 * @property {number} graphicHeight
 * @property {number} graphicWidth
 * @property {string} fillColor
 * @property {number} fillOpacity
 * @property {number} pointRadius
 * @property {number} rotation
 * @property {string} strokeColor
 * @property {number} strokeOpacity
 * @property {number} strokeWidth
 * @property {string} graphicName
 */

/**
 * extends {MapFishPrintSymbolizer}
 * @typedef {Object} MapFishPrintSymbolizerPolygon
 * @property {string} type (MapFishPrintSymbolizer)
 * @property {string} fillColor
 * @property {number} fillOpacity
 * @property {string} strokeColor
 * @property {number} strokeOpacity
 * @property {number} strokeWidth
 * @property {string} strokeDashstyle
 */

/**
 * extends {MapFishPrintSymbolizer}
 * @typedef {Object} MapFishPrintSymbolizerText
 * @property {string} type (MapFishPrintSymbolizer)
 * @property {string} label
 * @property {string} labelAlign
 * @property {string} labelRotation
 * @property {string} fontWeight
 * @property {string} fontSize
 * @property {string} fontFamily
 * @property {number} labelXOffset
 * @property {number} labelYOffset
 * @property {string} haloColor
 * @property {number} haloOpacity
 * @property {number} haloRadius
 * @property {string} fontColor
 */

/**
 * @typedef {Object} MapFishPrintSMTP
 * @property {string} to Email address
 */

/**
 * @typedef {Object} MapFishPrintLegend
 * @property {MapFishPrintLegendClass[]} classes
 */

/**
 * @typedef {Object} MapFishPrintLegendClass
 * @property {string} name
 * @property {string[]} icons
 */

/**
 * @hidden
 * @type {null}
 */
export const nothing = null;
