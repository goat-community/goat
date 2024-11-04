/* eslint-disable @typescript-eslint/no-explicit-any */
/* eslint-disable @typescript-eslint/ban-ts-comment */
// Copyright 2005-present, OpenLayers Contributors All rights reserved.
// Copyright MIT (c) Gastón Zalba.

import XML from 'ol/format/XML.js';
import {
  getAllTextContent,
  makeArrayPusher,
  makeObjectPropertyPusher,
  makeObjectPropertySetter,
  makeStructureNS,
  pushParseAndPop,
} from 'ol/xml.js';
import { readHref } from 'ol/format/xlink.js';
import { readString } from 'ol/format/xsd.js';


export type Parser = (arg0: Element, arg1: Array<any>) => void;


/**
 * @typedef {function(Element, Array<*>): void} Parser
 */

/**
 * @const
 * @type {Object<string,string>}
 */
const VERSIONS = {
  _200: '2.0.0',
  _110: '1.1.0',
  _100: '1.0.0',
};

/**
 * @param {Array<*>} objectStack Object stack.
 * @return {string} WFS version number
 */
function getVersion(objectStack) {
  return objectStack[0].version;
}
/**
 * @const
 * @type {Array<null|string>}
 */
const NAMESPACE_URIS = [
  "",
  'http://www.opengis.net/fes/2.0',
  'http://www.opengis.net/ows/1.1',
  'http://www.opengis.net/ows',
  'http://www.opengis.net/wfs',
  'http://www.opengis.net/wfs/2.0',
  'http://www.opengis.net/ogc',
  'http://www.opengis.net/gml',
  'http://www.opengis.net/gml/3.2',
];

/**
 * @const
 * @type {Object<string, Object<string,Object<string, import("ol/xml.js").Parser>>>}
 */
const PARSERS = {
  [VERSIONS._200]: makeStructureNS(NAMESPACE_URIS, {
    ServiceIdentification: makeObjectPropertySetter(readServiceIdentification),
    ServiceProvider: makeObjectPropertySetter(readServiceProvider),
    OperationsMetadata: makeObjectPropertySetter(readOperationsMetadata),
    FeatureTypeList: makeObjectPropertySetter(readFeatureTypeList),
    Filter_Capabilities: makeObjectPropertySetter(readFilter_Capabilities),
  }),
  [VERSIONS._110]: makeStructureNS(NAMESPACE_URIS, {
    ServiceIdentification: makeObjectPropertySetter(readServiceIdentification),
    ServiceProvider: makeObjectPropertySetter(readServiceProvider),
    OperationsMetadata: makeObjectPropertySetter(readOperationsMetadata),
    FeatureTypeList: makeObjectPropertySetter(readFeatureTypeList),
    Filter_Capabilities: makeObjectPropertySetter(readFilter_Capabilities),
  }),
  [VERSIONS._100]: makeStructureNS(NAMESPACE_URIS, {
    Service: makeObjectPropertySetter(readServiceIdentification),
    Capability: makeObjectPropertySetter(readCapability),
    FeatureTypeList: makeObjectPropertySetter(readFeatureTypeList),
    Filter_Capabilities: makeObjectPropertySetter(readFilter_Capabilities),
  }),
};

/**
 * @classdesc
 * Format for reading WFS capabilities data
 *
 * @api
 */
class WFSCapabilities extends XML {
  /**
  * @type {string|undefined}
  */
  version: string | undefined;

  constructor() {
    super();

    /**
     * @type {string|undefined}
     */
    this.version = undefined;
  }

  /**
   * @param {Element} node Node.
   * @return {Object} Object
   */
  readFromNode(node) {
    this.version = node.getAttribute('version').trim()
    const wfsCapabilityObject = pushParseAndPop(
      {
        version: this.version,
      },
      PARSERS[this.version || '2.0.0'],
      node,
      []
    );
    return wfsCapabilityObject ? wfsCapabilityObject : null;
  }
}

/**
 * @const
 * @type {Object<string, Object<string, import("ol/xml.js").Parser>>}
 */
// @ts-ignore
const SERVICE_IDENTIFICATION_PARSERS = makeStructureNS(NAMESPACE_URIS, {
  Name: makeObjectPropertySetter(readString),
  Title: makeObjectPropertySetter(readString),
  Abstract: makeObjectPropertySetter(readString),
  Keywords: makeObjectPropertySetter(function (node, objectStack) {
    const version = getVersion(objectStack);
    return version === VERSIONS._100
      ? readJoinedList(node)
      : readKeywordList(node, objectStack);
  }),
  ServiceType: makeObjectPropertySetter(readString),
  ServiceTypeVersion: makeObjectPropertySetter(readString),
  Fees: makeObjectPropertySetter(readString),
  AccessConstraints: makeObjectPropertySetter(readString),
  OnlineResource: makeObjectPropertySetter(readString),
});

/**
 * @const
 * @type {Object<string, Object<string, import("ol/xml.js").Parser>>}
 */
// @ts-ignore
const SERVICE_PROVIDER_PARSERS = makeStructureNS(NAMESPACE_URIS, {
  ProviderName: makeObjectPropertySetter(readString),
  ServiceContact: makeObjectPropertySetter(readServiceContact),
});

/**
 * @const
 * @type {Object<string, Object<string, import("ol/xml.js").Parser>>}
 */
// @ts-ignore
const OPERATIONS_METADATA_PARSERS = makeStructureNS(NAMESPACE_URIS, {
  Operation: makeObjectPropertyPusher(readNamedOperation),
  Constraint: makeObjectPropertyPusher(readNamedConstraint),
});

/**
 * @const
 * @type {Object<string, Object<string, import("ol/xml.js").Parser>>}
 */
// @ts-ignore
const CAPABILITY_PARSERS = makeStructureNS(NAMESPACE_URIS, {
  Request: makeObjectPropertySetter(readRequests),
});

/**
 * @const
 * @type {Object<string, Object<string, import("ol/xml.js").Parser>>}
 */
// @ts-ignore
const SERVICE_CONTACT_PARSERS = makeStructureNS(NAMESPACE_URIS, {
  IndividualName: makeObjectPropertySetter(readString),
  PositionName: makeObjectPropertySetter(readString),
  ContactInfo: makeObjectPropertySetter(readContactInfo),
});

/**
 * @const
 * @type {Object<string, Object<string, import("ol/xml.js").Parser>>}
 */
// @ts-ignore
const CONTACT_INFO_PARSERS = makeStructureNS(NAMESPACE_URIS, {
  Phone: makeObjectPropertySetter(readPhone),
  Address: makeObjectPropertySetter(readAddress),
});

/**
 * @const
 * @type {Object<string, Object<string, import("ol/xml.js").Parser>>}
 */
// @ts-ignore
const PHONE_PARSERS = makeStructureNS(NAMESPACE_URIS, {
  Voice: makeObjectPropertySetter(readString),
  Facsimile: makeObjectPropertySetter(readString),
});

/**
 * @const
 * @type {Object<string, Object<string, import("ol/xml.js").Parser>>}
 */
// @ts-ignore
const ADDRESS_PARSERS = makeStructureNS(NAMESPACE_URIS, {
  DeliveryPoint: makeObjectPropertySetter(readString),
  City: makeObjectPropertySetter(readString),
  AdministrativeArea: makeObjectPropertySetter(readString),
  PostalCode: makeObjectPropertySetter(readString),
  Country: makeObjectPropertySetter(readString),
  ElectronicMailAddress: makeObjectPropertySetter(readString),
});

/**
 * @const
 * @type {Object<string, Object<string, import("ol/xml.js").Parser>>}
 */
// @ts-ignore
const FEATURE_TYPE_LIST_PARSERS = makeStructureNS(NAMESPACE_URIS, {
  FeatureType: makeArrayPusher(readFeatureType),
});

/**
 * @const
 * @type {Object<string, Object<string, import("ol/xml.js").Parser>>}
 */
// @ts-ignore
const FEATURE_TYPE_LIST_100_PARSERS = makeStructureNS(NAMESPACE_URIS, {
  Operations: makeObjectPropertySetter(readTagList),
  FeatureType: makeObjectPropertyPusher(readFeatureType),
});

/**
 * @const
 * @type {Object<string, Object<string, import("ol/xml.js").Parser>>}
 */
// @ts-ignore
const FEATURE_TYPE_LIST_110_PARSERS = makeStructureNS(NAMESPACE_URIS, {
  Operations: makeObjectPropertySetter(readOperation_110),
  FeatureType: makeObjectPropertyPusher(readFeatureType),
});

/**
 * @const
 * @type {Object<string, Object<string, import("ol/xml.js").Parser>>}
 */
// @ts-ignore
const FEATURE_TYPE_PARSERS = makeStructureNS(NAMESPACE_URIS, {
  Name: makeObjectPropertySetter(readString),
  Title: makeObjectPropertySetter(readString),
  Abstract: makeObjectPropertySetter(readString),
  Keywords: makeObjectPropertySetter(function (node, objectStack) {
    const version = getVersion(objectStack);
    return version === VERSIONS._100
      ? readJoinedList(node)
      : readKeywordList(node, objectStack);
  }),
  DefaultSRS: makeObjectPropertySetter(readString),
  DefaultCRS: makeObjectPropertySetter(readString), // 1.1.0
  OtherSRS: makeObjectPropertyPusher(readString), // 1.1.0
  SRS: makeObjectPropertySetter(readString),
  WGS84BoundingBox: makeObjectPropertySetter(readWGS84BoundingBox),
  MetadataURL: makeObjectPropertySetter(readHrefOrValue),
  LatLongBoundingBox: makeObjectPropertySetter(readLatLongBoundingBox), // 1.0.0
});

/**
 * @const
 * @type {Object<string, Object<string, import("ol/xml.js").Parser>>}
 */
// @ts-ignore
const OPERATION_PARSERS = makeStructureNS(NAMESPACE_URIS, {
  DCP: makeObjectPropertySetter(readDCP),
  Parameter: makeObjectPropertyPusher(readNamedParameter),
});

/**
 * @const
 * @type {Object<string, Object<string, import("ol/xml.js").Parser>>}
 */
// @ts-ignore
const OPERATION_110_PARSERS = makeStructureNS(NAMESPACE_URIS, {
  Operation: makeArrayPusher(readString),
});

/**
 * @const
 * @type {Object<string, Object<string, import("ol/xml.js").Parser>>}
 */
// @ts-ignore
const REQUEST_PARSERS = makeStructureNS(NAMESPACE_URIS, {
  DCPType: makeObjectPropertyMerger(readDCPType),
  SchemaDescriptionLanguage: makeObjectPropertySetter(readTagList),
  ResultFormat: makeObjectPropertySetter(readTagList),
});

/**
 * @const
 * @type {Object<string, Object<string, import("ol/xml.js").Parser>>}
 */
// @ts-ignore
const PARAMETER_PARSERS = makeStructureNS(NAMESPACE_URIS, {
  Value: makeObjectPropertyPusher(readString),
  AllowedValues: makeObjectPropertySetter(readValueList),
});

/**
 * @const
 * @type {Object<string, Object<string, import("ol/xml.js").Parser>>}
 */
// @ts-ignore
const CONSTRAINT_PARSERS = makeStructureNS(NAMESPACE_URIS, {
  NoValues: makeObjectPropertySetter(readString),
  DefaultValue: makeObjectPropertySetter(readString),
  AllowedValues: makeObjectPropertySetter(readValueList),
});

/**
 * @const
 * @type {Object<string, Object<string, import("ol/xml.js").Parser>>}
 */
// @ts-ignore
const HTTP_PARSERS = makeStructureNS(NAMESPACE_URIS, {
  Get: makeObjectPropertySetter(readHref),
  Post: makeObjectPropertySetter(readHref),
});

/**
 * @const
 * @type {Object<string, Object<string, import("ol/xml.js").Parser>>}
 */
// @ts-ignore
const HTTP_100_PARSERS = makeStructureNS(NAMESPACE_URIS, {
  Get: makeObjectPropertySetter(readOnline),
  Post: makeObjectPropertySetter(readOnline),
});

/**
 * @const
 * @type {Object<string, Object<string, import("ol/xml.js").Parser>>}
 */
// @ts-ignore
const WGS84_BOUNDINGBOX_PARSERS = makeStructureNS(NAMESPACE_URIS, {
  LowerCorner: makeObjectPropertySetter(readStringCoords),
  UpperCorner: makeObjectPropertySetter(readStringCoords),
});

/**
 * @const
 * @type {Object<string, Object<string, import("ol/xml.js").Parser>>}
 */
// @ts-ignore
const DCP_PARSERS = makeStructureNS(NAMESPACE_URIS, {
  HTTP: makeObjectPropertySetter(readHTTP),
});

/**
 * @const
 * @type {Object<string, Object<string, import("ol/xml.js").Parser>>}
 */
// @ts-ignore
const DCPTYPE_PARSERS = makeStructureNS(NAMESPACE_URIS, {
  HTTP: makeObjectPropertySetter(readHTTP_100),
});

/**
 * @const
 * @type {Object<string, Object<string, import("ol/xml.js").Parser>>}
 */
// @ts-ignore
const KEYWORDLIST_PARSERS = makeStructureNS(NAMESPACE_URIS, {
  Keyword: makeArrayPusher(readString),
});

/**
 * @const
 * @type {Object<string, Object<string, import("ol/xml.js").Parser>>}
 */
// @ts-ignore
const VALUELIST_PARSERS = makeStructureNS(NAMESPACE_URIS, {
  Value: makeArrayPusher(readString),
});

/**
 * @const
 * @type {Object<string, Object<string, import("ol/xml.js").Parser>>}
 */
// @ts-ignore
const FILTER_CAPABILITIES_PARSERS = makeStructureNS(NAMESPACE_URIS, {
  Conformance: makeObjectPropertySetter(readConformance),
  Id_Capabilities: makeObjectPropertySetter(readId_Capabilities),
  Scalar_Capabilities: makeObjectPropertySetter(readScalarCapabilities),
  Spatial_Capabilities: makeObjectPropertySetter(readSpatialCapabilities),
  Temporal_Capabilities: makeObjectPropertySetter(readTemporalCapabilities),
  Functions: makeObjectPropertySetter(readFunctions),
});

/**
 * @const
 * @type {Object<string, Object<string, import("ol/xml.js").Parser>>}
 */
// @ts-ignore
const CONFORMANCE_PARSERS = makeStructureNS(NAMESPACE_URIS, {
  Constraint: makeObjectPropertyPusher(readNamedConstraint),
});

/**
 * @const
 * @type {Object<string, Object<string, import("ol/xml.js").Parser>>}
 */
// @ts-ignore
const ID_CAPABILITIES_PARSERS = makeStructureNS(NAMESPACE_URIS, {
  ResourceIdentifier: makeArrayPusher(readNamedResourceIdentifier),
});

/**
 * @const
 * @type {Object<string, Object<string, import("ol/xml.js").Parser>>}
 */
// @ts-ignore
const SCALAR_CAPABILITIES_PARSERS = makeStructureNS(NAMESPACE_URIS, {
  LogicalOperators: makeObjectPropertySetter(readLogicalOperators),
  ComparisonOperators: makeObjectPropertySetter(readComparisonOperators),
});

/**
 * @const
 * @type {Object<string, Object<string, import("ol/xml.js").Parser>>}
 */
// @ts-ignore
const SCALAR_CAPABILITIES_110_PARSERS = makeStructureNS(NAMESPACE_URIS, {
  LogicalOperators: makeObjectPropertySetter(readString),
  ComparisonOperators: makeObjectPropertySetter(readComparisonOperators),
  ArithmeticOperators: makeObjectPropertySetter(readArithmetic_Operators),
});

/**
 * @const
 * @type {Object<string, Object<string, import("ol/xml.js").Parser>>}
 */
// @ts-ignore
const SCALAR_CAPABILITIES_100_PARSERS = makeStructureNS(NAMESPACE_URIS, {
  Logical_Operators: makeObjectPropertySetter(readString),
  Comparison_Operators: makeObjectPropertySetter(readTagList),
  Arithmetic_Operators: makeObjectPropertySetter(readArithmetic_Operators),
});

/**
 * @const
 * @type {Object<string, Object<string, import("ol/xml.js").Parser>>}
 */
// @ts-ignore
const SPATIAL_CAPABILITIES_PARSERS = makeStructureNS(NAMESPACE_URIS, {
  GeometryOperands: makeObjectPropertySetter(readGeometryOperands),
  SpatialOperators: makeObjectPropertySetter(readSpatialOperators),
});

/**
 * @const
 * @type {Object<string, Object<string, import("ol/xml.js").Parser>>}
 */
// @ts-ignore
const SPATIAL_CAPABILITIES_100_PARSERS = makeStructureNS(NAMESPACE_URIS, {
  Spatial_Operators: makeObjectPropertySetter(readTagList),
});

/**
 * @const
 * @type {Object<string, Object<string, import("ol/xml.js").Parser>>}
 */
// @ts-ignore
const TEMPORAL_CAPABILITIES_PARSERS = makeStructureNS(NAMESPACE_URIS, {
  TemporalOperands: makeObjectPropertySetter(readTemporalOperands),
  TemporalOperators: makeObjectPropertySetter(readTemporalOperators),
});

/**
 * @const
 * @type {Object<string, Object<string, import("ol/xml.js").Parser>>}
 */
// @ts-ignore
const FUNCTIONS_PARSERS = makeStructureNS(NAMESPACE_URIS, {
  Function: makeArrayPusher(readNamedFunction),
});

/**
 * @const
 * @type {Object<string, Object<string, import("ol/xml.js").Parser>>}
 */
// @ts-ignore
const FUNCTIONS_100_PARSERS = makeStructureNS(NAMESPACE_URIS, {
  Function_Names: makeObjectPropertySetter(readFunction_Names), // 1.0.0
  FunctionNames: makeObjectPropertySetter(readFunction_Names), // 1.1.0
});

/**
 * @const
 * @type {Object<string, Object<string, import("ol/xml.js").Parser>>}
 */
// @ts-ignore
const FUNCTION_NAMES_PARSERS = makeStructureNS(NAMESPACE_URIS, {
  FunctionName: makeArrayPusher(readFunction_Name), // 1.1.0
  Function_Name: makeArrayPusher(readFunction_Name), // 1.0.0
});

/**
 * @const
 * @type {Object<string, Object<string, import("ol/xml.js").Parser>>}
 */
// @ts-ignore
const FUNCTION_PARSERS = makeStructureNS(NAMESPACE_URIS, {
  Returns: makeObjectPropertySetter(readString),
  Arguments: makeObjectPropertySetter(readArguments),
});

/**
 * @const
 * @type {Object<string, Object<string, import("ol/xml.js").Parser>>}
 */
// @ts-ignore
const ARGUMENTS_PARSERS = makeStructureNS(NAMESPACE_URIS, {
  Argument: makeArrayPusher(readNamedArgument),
});

/**
 * @const
 * @type {Object<string, Object<string, import("ol/xml.js").Parser>>}
 */
// @ts-ignore
const ARGUMENT_PARSERS = makeStructureNS(NAMESPACE_URIS, {
  Type: makeObjectPropertySetter(readString),
});

/**
 * @const
 * @type {Object<string, Object<string, import("ol/xml.js").Parser>>}
 */
// @ts-ignore
const LOGICAL_OPERATORS_PARSERS = makeStructureNS(NAMESPACE_URIS, {
  LogicalOperator: makeArrayPusher(readNamedOnly),
});

/**
 * @const
 * @type {Object<string, Object<string, import("ol/xml.js").Parser>>}
 */
// @ts-ignore
const COMPARISON_OPERATORS_PARSERS = makeStructureNS(NAMESPACE_URIS, {
  ComparisonOperator: makeArrayPusher(readNamedOrValueOnly),
});

/**
 * @const
 * @type {Object<string, Object<string, import("ol/xml.js").Parser>>}
 */
// @ts-ignore
const ARITHMETIC_OPERATORS_PARSERS = makeStructureNS(NAMESPACE_URIS, {
  Simple_Arithmetic: makeObjectPropertySetter(readString),
  SimpleArithmetic: makeObjectPropertySetter(readString),
  Functions: makeObjectPropertySetter(readFunctions100),
});

/**
 * @const
 * @type {Object<string, Object<string, import("ol/xml.js").Parser>>}
 */
// @ts-ignore
const GEOMETRY_OPERANDS_PARSERS = makeStructureNS(NAMESPACE_URIS, {
  GeometryOperand: makeArrayPusher(readNamedOrValueOnly),
});

/**
 * @const
 * @type {Object<string, Object<string, import("ol/xml.js").Parser>>}
 */
// @ts-ignore
const SPATIAL_OPERATORS_PARSERS = makeStructureNS(NAMESPACE_URIS, {
  SpatialOperator: makeArrayPusher(readNamedOnly),
});

/**
 * @const
 * @type {Object<string, Object<string, import("ol/xml.js").Parser>>}
 */
// @ts-ignore
const TEMPORAL_OPERANDS_PARSERS = makeStructureNS(NAMESPACE_URIS, {
  TemporalOperand: makeArrayPusher(readNamedOnly),
});

/**
 * @const
 * @type {Object<string, Object<string, import("ol/xml.js").Parser>>}
 */
// @ts-ignore
const TEMPORAL_OPERATORS_PARSERS = makeStructureNS(NAMESPACE_URIS, {
  TemporalOperator: makeArrayPusher(readNamedOnly),
});

/**
 * @param {Element} node Node.
 * @param {Array<*>} objectStack Object stack.
 * @return {Object|undefined} Service Identification object.
 */
function readServiceIdentification(node, objectStack) {
  return pushParseAndPop({}, SERVICE_IDENTIFICATION_PARSERS, node, objectStack);
}

/**
 * @param {Element} node Node.
 * @param {Array<*>} objectStack Object stack.
 * @return {Object|undefined} Service Provider object.
 */
function readServiceProvider(node, objectStack) {
  return pushParseAndPop({}, SERVICE_PROVIDER_PARSERS, node, objectStack);
}

/**
 * @param {Element} node Node.
 * @param {Array<*>} objectStack Object stack.
 * @return {Object|undefined} Operations Metadata object.
 */
function readOperationsMetadata(node, objectStack) {
  return pushParseAndPop({}, OPERATIONS_METADATA_PARSERS, node, objectStack);
}

/**
 * @param {Element} node Node.
 * @param {Array<*>} objectStack Object stack.
 * @return {Object|undefined} Operations Metadata object.
 */
function readCapability(node, objectStack) {
  return pushParseAndPop({}, CAPABILITY_PARSERS, node, objectStack);
}

/**
 * @param {Element} node Node.
 * @param {Array<*>} objectStack Object stack.
 * @return {Object|undefined} FeatureType list.
 */
function readFeatureTypeList(node, objectStack) {
  const version = getVersion(objectStack);
  let featureTypeParser;
  if (version === VERSIONS._100) {
    featureTypeParser = FEATURE_TYPE_LIST_100_PARSERS;
  } else if (version === VERSIONS._110) {
    featureTypeParser = FEATURE_TYPE_LIST_110_PARSERS;
  } else {
    featureTypeParser = FEATURE_TYPE_LIST_PARSERS;
  }
  return pushParseAndPop(
    version === VERSIONS._100 || version === VERSIONS._110 ? {} : [],
    featureTypeParser,
    node,
    objectStack
  );
}

/**
 * @param {Element} node Node.
 * @param {Array<*>} objectStack Object stack.
 * @return {Object|undefined} Serrvice contact object.
 */
function readServiceContact(node, objectStack) {
  return pushParseAndPop({}, SERVICE_CONTACT_PARSERS, node, objectStack);
}

/**
 * @param {Element} node Node.
 * @param {Array<*>} objectStack Object stack.
 * @return {Object|undefined} Contact info object.
 */
function readContactInfo(node, objectStack) {
  return pushParseAndPop({}, CONTACT_INFO_PARSERS, node, objectStack);
}

/**
 * @param {Element} node Node.
 * @param {Array<*>} objectStack Object stack.
 * @return {Object|undefined} Contact Phone object.
 */
function readPhone(node, objectStack) {
  return pushParseAndPop({}, PHONE_PARSERS, node, objectStack);
}

/**
 * @param {Element} node Node.
 * @param {Array<*>} objectStack Object stack.
 * @return {Object|undefined} Contact address object.
 */
function readAddress(node, objectStack) {
  return pushParseAndPop({}, ADDRESS_PARSERS, node, objectStack);
}

/**
 * @param {Element} node Node.
 * @param {Array<*>} objectStack Object stack.
 * @return {Object|undefined} DCP object.
 */
function readDCP(node, objectStack) {
  return pushParseAndPop({}, DCP_PARSERS, node, objectStack);
}

/**
 * @param {Element} node Node.
 * @param {Array<*>} objectStack Object stack.
 * @return {Object|undefined} DCP object.
 */
function readDCPType(node, objectStack) {
  return pushParseAndPop({}, DCPTYPE_PARSERS, node, objectStack);
}

/**
 * @param {Element} node Node.
 * @param {Array<*>} objectStack Object stack.
 * @return {Object|undefined} Operation object.
 */
function readOperation(node, objectStack) {
  return pushParseAndPop({}, OPERATION_PARSERS, node, objectStack);
}

/**
 * @param {Element} node Node.
 * @param {Array<*>} objectStack Object stack.
 * @return {Object|undefined} Operation object.
 */
function readOperation_110(node, objectStack) {
  return pushParseAndPop([], OPERATION_110_PARSERS, node, objectStack);
}

/**
 * @param {Element} node Node.
 * @param {Array<*>} objectStack Object stack.
 * @return {Object|undefined} Operation object.
 */
function readRequest(node, objectStack) {
  return pushParseAndPop({}, REQUEST_PARSERS, node, objectStack);
}

/**
 * @param {Element} node Node.
 * @param {Array<*>} objectStack Object stack.
 * @return {Object|undefined} Parameter object.
 */
function readParameter(node, objectStack) {
  return getVersion(objectStack) === VERSIONS._110
    ? pushParseAndPop({}, PARAMETER_PARSERS, node, objectStack)
    : pushParseAndPop({}, PARAMETER_PARSERS, node, objectStack);
}

/**
 * @param {Element} node Node.
 * @param {Array<*>} objectStack Object stack.
 * @return {Object|undefined} Constraint object.
 */
function readConstraint(node, objectStack) {
  return pushParseAndPop({}, CONSTRAINT_PARSERS, node, objectStack);
}

/**
 * @param {Element} node Node.
 * @param {Array<*>} objectStack Object stack.
 * @return {Object|undefined} HTTP object.
 */
function readHTTP(node, objectStack) {
  return pushParseAndPop({}, HTTP_PARSERS, node, objectStack);
}

/**
 * @param {Element} node Node.
 * @param {Array<*>} objectStack Object stack.
 * @return {Object|undefined} HTTP object.
 */
function readHTTP_100(node, objectStack) {
  return pushParseAndPop({}, HTTP_100_PARSERS, node, objectStack);
}

/**
 * @param {Element} node Node.
 * @param {Array<*>} objectStack Object stack.
 * @return {Object|undefined} DCP object.
 */
function readFunction_Names(node, objectStack) {
  return pushParseAndPop([], FUNCTION_NAMES_PARSERS, node, objectStack);
}

/**
 * @param {Element} node Node.
 * @param {Array<*>} objectStack Object stack.
 * @return {Object|undefined} Named operation object.
 */
function readNamedOperation(node, objectStack) {
  const operation = readOperation(node, objectStack);
  if (operation) {
    operation['name'] = node.getAttribute('name');
    return operation;
  }
  return undefined;
}

/**
 * @param {Element} node Node.
 * @param {Array<*>} objectStack Object stack.
 * @return {Array|undefined} Request object.
 */
function readRequests(node, objectStack) {
  const arr = [] as any[];
  for (const n of node.children) {
    const request = readRequest(n, objectStack);
    if (request) {
      request['name'] = n.tagName;
      arr.push(request);
    }
  }
  if (arr.length) {
    return arr;
  }
  return undefined;
}

/**
 * @param {Element} node Node.
 * @param {Array<*>} objectStack Object stack.
 * @return {Object|undefined} Named Function object.
 */
function readNamedFunction(node, objectStack) {
  const func = readFunction(node, objectStack);
  if (func) {
    func['name'] = node.getAttribute('name');
    return func;
  }
  return undefined;
}

/**
 * @param {Element} node Node.
 * @param {Array<*>} objectStack Object stack.
 * @return {Object|undefined} Named Function object.
 */
function readFunction_Name(node, objectStack) {
  const func = readFunction(node, objectStack);
  if (func) {
    func['name'] = readString(node);
    func['nArgs'] = Number(node.getAttribute('nArgs'));
    return func;
  }
  return undefined;
}

/**
 * @param {Element} node Node.
 * @param {Array<*>} objectStack Object stack.
 * @return {Object|undefined} Named argument object.
 */
function readNamedArgument(node, objectStack) {
  const argument = readArgument(node, objectStack);
  if (argument) {
    argument['name'] = node.getAttribute('name');
    return argument;
  }
  return undefined;
}

/**
 * @param {Element} node Node.
 * @param {Array<*>} objectStack Object stack.
 * @return {Object|undefined} Named Parameter object.
 */
function readNamedParameter(node, objectStack) {
  const parameter = readParameter(node, objectStack);
  if (parameter) {
    parameter['name'] = node.getAttribute('name');
    return parameter;
  }
  return undefined;
}

/**
 * @param {Element} node Node.
 * @param {Array<*>} objectStack Object stack.
 * @return {Object|undefined} Named Constraint object.
 */
function readNamedConstraint(node, objectStack) {
  const constraint = readConstraint(node, objectStack);
  if (constraint) {
    constraint['name'] = node.getAttribute('name');
    return constraint;
  }
  return undefined;
}

/**
 * @param {Element} node Node.
 * @return {string|undefined} Node name attribute string.
 */
function readNamedOnly(node) {
  return node.getAttribute('name') || undefined;
}

/**
 * @param {Element} node Node.
 * @return {string|undefined} Node name or value attribute string (useful for compatibility between versions)
 */
function readNamedOrValueOnly(node) {
  return readNamedOnly(node) || readString(node) || undefined;
}

/**
 * @param {Element} node Node.
 * @return {string|undefined} Node href or value attribute string (useful for compatibility between versions)
 */
function readHrefOrValue(node) {
  return readHref(node) || readString(node) || undefined;
}

/**
 * @param {Element} node Node.
 * @return {Object|undefined} Named Resource Identifier object.
 */
function readNamedResourceIdentifier(node) {
  return {
    name: node.getAttribute('name'),
  };
}

/**
 * @param {Element} node Node.
 * @param {Array<*>} objectStack Object stack.
 * @return {Object|undefined} WGS84 BoundingBox resource object.
 */
function readWGS84BoundingBox(node, objectStack) {
  return pushParseAndPop({}, WGS84_BOUNDINGBOX_PARSERS, node, objectStack);
}

/**
 * @param {Element} node Node.
 * @param {Array<*>} objectStack Object stack.
 * @return {Array<number>|undefined} LatLong BoundingBox resource object.
 */
function readLatLongBoundingBox(node, _objectStack) {
  return [
    Number(node.getAttribute('minx')),
    Number(node.getAttribute('miny')),
    Number(node.getAttribute('maxx')),
    Number(node.getAttribute('maxy')),
  ];
}

/**
 * @param {Element} node Node.
 * @param {Array<*>} objectStack Object stack.
 * @return {Array<string>|undefined} Keyword list.
 */
function readKeywordList(node, objectStack) {
  return pushParseAndPop([], KEYWORDLIST_PARSERS, node, objectStack);
}

/**
 * @param {Element} node Node.
 * @param {Array<*>} objectStack Object stack.
 * @return {Array<string>|undefined} Value list.
 */
function readValueList(node, objectStack) {
  return pushParseAndPop([], VALUELIST_PARSERS, node, objectStack);
}

/**
 * @param {Element} node Node.
 * @param {Array<*>} objectStack Object stack.
 * @return {Array<string>|undefined} Value list.
 */
function readTagList(node, _objectStack) {
  const arr = [] as string[];
  for (const n of node.children) {
    const tagName = n.tagName;
    // Remove namespace
    const splittedTagName = tagName.split(':');
    arr.push(splittedTagName[splittedTagName.length - 1]);
  }
  if (arr.length) {
    return arr;
  }
  return undefined;
}

/**
 * @param {Element} node Node.
 * @param {Array<*>} objectStack Object stack.
 * @return {Object|undefined} FeatureTyoe object.
 */
function readFeatureType(node, objectStack) {
  return pushParseAndPop({}, FEATURE_TYPE_PARSERS, node, objectStack);
}

/**
 * @param {Element} node Node.
 * @param {Array<*>} objectStack Object stack.
 * @return {Object|undefined} FilterCapabilities object.
 */
function readFilter_Capabilities(node, objectStack) {
  return pushParseAndPop({}, FILTER_CAPABILITIES_PARSERS, node, objectStack);
}

/**
 * @param {Element} node Node.
 * @param {Array<*>} objectStack Object stack.
 * @return {Object|undefined} Conformance object.
 */
function readConformance(node, objectStack) {
  return pushParseAndPop({}, CONFORMANCE_PARSERS, node, objectStack);
}

/**
 * @param {Element} node Node.
 * @param {Array<*>} objectStack Object stack.
 * @return {Object|undefined} Id Capabilities object.
 */
function readId_Capabilities(node, objectStack) {
  return getVersion(objectStack) === VERSIONS._110
    ? readTagList(node, objectStack)
    : pushParseAndPop([], ID_CAPABILITIES_PARSERS, node, objectStack);
}

/**
 * @param {Element} node Node.
 * @param {Array<*>} objectStack Object stack.
 * @return {Object|undefined} Scalar Capabilities object.
 */
function readScalarCapabilities(node, objectStack) {
  let scalarParser;
  const version = getVersion(objectStack);
  if (version === VERSIONS._100) {
    scalarParser = SCALAR_CAPABILITIES_100_PARSERS;
  } else if (version === VERSIONS._110) {
    scalarParser = SCALAR_CAPABILITIES_110_PARSERS;
  } else {
    scalarParser = SCALAR_CAPABILITIES_PARSERS;
  }
  return pushParseAndPop({}, scalarParser, node, objectStack);
}

/**
 * @param {Element} node Node.
 * @param {Array<*>} objectStack Object stack.
 * @return {Object|undefined} Spatial Capabilities object.
 */
function readSpatialCapabilities(node, objectStack) {
  return pushParseAndPop(
    {},
    getVersion(objectStack) === VERSIONS._100
      ? SPATIAL_CAPABILITIES_100_PARSERS
      : SPATIAL_CAPABILITIES_PARSERS,
    node,
    objectStack
  );
}

/**
 * @param {Element} node Node.
 * @param {Array<*>} objectStack Object stack.
 * @return {Object|undefined} Temporal Capabilities object.
 */
function readTemporalCapabilities(node, objectStack) {
  return pushParseAndPop({}, TEMPORAL_CAPABILITIES_PARSERS, node, objectStack);
}

/**
 * @param {Element} node Node.
 * @param {Array<*>} objectStack Object stack.
 * @return {Array<string>|undefined} Functions array.
 */
function readFunctions(node, objectStack) {
  return pushParseAndPop([], FUNCTIONS_PARSERS, node, objectStack);
}

/**
 * @param {Element} node Node.
 * @param {Array<*>} objectStack Object stack.
 * @return {Object|undefined} Functions object.
 */
function readFunctions100(node, objectStack) {
  return pushParseAndPop({}, FUNCTIONS_100_PARSERS, node, objectStack);
}

/**
 * @param {Element} node Node.
 * @param {Array<*>} objectStack Object stack.
 * @return {Object|undefined} Function object.
 */
function readFunction(node, objectStack) {
  return pushParseAndPop({}, FUNCTION_PARSERS, node, objectStack);
}

/**
 * @param {Element} node Node.
 * @param {Array<*>} objectStack Object stack.
 * @return {Array<string>|undefined} Logical Operators array.
 */
function readLogicalOperators(node, objectStack) {
  return pushParseAndPop([], LOGICAL_OPERATORS_PARSERS, node, objectStack);
}

/**
 * @param {Element} node Node.
 * @param {Array<*>} objectStack Object stack.
 * @return {Array<string>|undefined} Comparison Operators array.
 */
function readComparisonOperators(node, objectStack) {
  return pushParseAndPop([], COMPARISON_OPERATORS_PARSERS, node, objectStack);
}

/**
 * @param {Element} node Node.
 * @param {Array<*>} objectStack Object stack.
 * @return {Object|undefined} Arithmetic Operators object.
 */
function readArithmetic_Operators(node, objectStack) {
  return pushParseAndPop({}, ARITHMETIC_OPERATORS_PARSERS, node, objectStack);
}

/**
 * @param {Element} node Node.
 * @param {Array<*>} objectStack Object stack.
 * @return {Array<string>|undefined} Geometry Operands array.
 */
function readGeometryOperands(node, objectStack) {
  return pushParseAndPop([], GEOMETRY_OPERANDS_PARSERS, node, objectStack);
}

/**
 * @param {Element} node Node.
 * @param {Array<*>} objectStack Object stack.
 * @return {Array<string>|undefined} Spatials Operators array.
 */
function readSpatialOperators(node, objectStack) {
  return pushParseAndPop([], SPATIAL_OPERATORS_PARSERS, node, objectStack);
}

/**
 * @param {Element} node Node.
 * @param {Array<*>} objectStack Object stack.
 * @return {Array<string>|undefined} Temporal Operands array.
 */
function readTemporalOperands(node, objectStack) {
  return pushParseAndPop([], TEMPORAL_OPERANDS_PARSERS, node, objectStack);
}

/**
 * @param {Element} node Node.
 * @param {Array<*>} objectStack Object stack.
 * @return {Array<string>|undefined} Temporal Operators array.
 */
function readTemporalOperators(node, objectStack) {
  return pushParseAndPop([], TEMPORAL_OPERATORS_PARSERS, node, objectStack);
}

/**
 * @param {Element} node Node.
 * @param {Array<*>} objectStack Object stack.
 * @return {Array<string>|undefined} Arguments array.
 */
function readArguments(node, objectStack) {
  return pushParseAndPop([], ARGUMENTS_PARSERS, node, objectStack);
}

/**
 * @param {Element} node Node.
 * @param {Array<*>} objectStack Object stack.
 * @return {Object|undefined} Argument object.
 */
function readArgument(node, objectStack) {
  return pushParseAndPop({}, ARGUMENT_PARSERS, node, objectStack);
}

/**
 * @param {Element} node Node.
 * @return {Array<number>|undefined} Coordinates array.
 */
function readStringCoords(node) {
  const coords = getAllTextContent(node, false).split(' ');
  if (coords.length) {
    return coords.map((c) => Number(c));
  }
  return undefined;
}

/**
 * @param {Node} node Node.
 * @param {string} separator separator
 * @return {Array|undefined} String array.
 */
function readJoinedList(node, separator = ', ') {
  const value = readString(node);
  if (!value) {
    return undefined;
  }
  const arr = value.split(separator);
  if (!arr || !arr.length) {
    return undefined;
  }
  return arr;
}

/**
 * @param {Element} node Node.
 * @return {string|undefined} online resource attribute.
 */
function readOnline(node) {
  return node.getAttribute('onlineResource');
}

/**
 * Make an object property merger function for adding a property to the
 * object at the top of the stack.
 * @param {function(this: T, Element, Array<*>): *} valueReader Value reader.
 * @param {string} [property] Property.
 * @param {T} [thisArg] The object to use as `this` in `valueReader`.
 * @return {Parser} Parser.
 * @template T
 */
function makeObjectPropertyMerger(valueReader, property?, thisArg?) {
  return (
    /**
     * @param {Element} node Node.
     * @param {Array<*>} objectStack Object stack.
     */
    function (node, objectStack) {
      const value = valueReader.call(
        thisArg !== undefined ? thisArg : this,
        node,
        objectStack
      );
      if (value !== undefined) {
        const object = /** @type {!Object} */ (
          objectStack[objectStack.length - 1]
        );
        const name = property !== undefined ? property : node.localName;
        for (const key of Object.keys(value)) {
          if (object[name] && key in object[name]) {
            object[name][key] = { ...object[name][key], ...value[key] };
          } else {
            object[name] = value;
          }
        }
      }
    }
  );
}
export default WFSCapabilities;
