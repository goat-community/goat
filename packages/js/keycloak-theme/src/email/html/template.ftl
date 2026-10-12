<#-- Branding from theme.properties; blank values count as unset. -->
<#assign brandName = (properties.brandName!"")?trim>
<#if !brandName?has_content><#assign brandName = "GOAT"></#if>
<#assign logoUrl = (properties.logoUrl!"")?trim>
<#assign contactUrl = (properties.contactUrl!"")?trim>
<#assign privacyUrl = (properties.privacyUrl!"")?trim>
<#assign appUrl = (properties.appUrl!"")?trim?remove_ending("/")>
<#assign assetsUrl = (properties.staticAssetsUrl!"")?trim?remove_ending("/")>
<#if !assetsUrl?has_content && appUrl?has_content><#assign assetsUrl = appUrl + "/assets"></#if>

<#macro brandMark>
  <#if logoUrl?has_content>
    <img
      alt="${brandName}"
      src="${logoUrl}"
      style="max-width: 140px"
      title=""
    />
  <#else>
    ${brandName}
  </#if>
</#macro>

<#-- artwork: file name under <assets>/img/email/, shown above the title. -->
<#macro emailLayout artwork="">
<!DOCTYPE html>
<html lang="${msg("emailLangCode")}" xmlns="http://www.w3.org/1999/xhtml" xmlns:o="urn:schemas-microsoft-com:office:office">
    <head>
        <meta http-equiv="X-UA-Compatible" content="IE=edge" />
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <meta name="viewport" content="width=device-width,initial-scale=1" />
        <meta name="x-apple-disable-message-reformatting">
        <title></title>
        <!--[if mso]>
        <noscript>
            <xml>
            <o:OfficeDocumentSettings>
                <o:AllowPNG />
                <o:PixelsPerInch>96</o:PixelsPerInch>
            </o:OfficeDocumentSettings>
            </xml>
        </noscript>
        <![endif]-->
    </head>
  <body
    style="
      font-family: Arial, Open Sans, Helvetica, Arial, sans-serif;
      text-align: center;
      word-spacing: normal;
      background-color: #f8f8f8;
      margin: 0;
      padding: 0;
    "
  >
    <table
      role="presentation"
      style="
        padding: 0;
        border-spacing: 0;
        width: 100%;
        margin-left: auto;
        margin-right: auto;
        max-width: 600px;
        text-align: center;
        align-items: center;
      "
    >
      <thead>
        <tr>
          <td>
            <#assign brandStyle = "display: inline-block; margin-top: 20px; margin-bottom: 20px; color: #4d4d4d; font-size: 22px; font-weight: 700; text-decoration: none;">
            <#if appUrl?has_content>
            <a href="${appUrl}" style="${brandStyle}"><@brandMark /></a>
            <#else>
            <span style="${brandStyle}"><@brandMark /></span>
            </#if>
          </td>
        </tr>
      </thead>
      <tbody style="background: #ffffff; background-color: #ffffff">
        <#if artwork?has_content && assetsUrl?has_content>
        <tr>
          <td style="padding-top: 40px;">
            <img
                alt=""
                src="${assetsUrl}/img/email/${artwork}"
                style="width: 250px"
            />
          </td>
        </tr>
        </#if>
        <#nested>
        <tr>
          <td style="padding-top: 40px">
            <p
              style="
                border-top: solid 7px #2bb381;
                margin: 0px auto;
                width: 100%;
              "
            ></p>
          </td>
        </tr>
      </tbody>
      <tfoot
        style="
          text-align: center;
          -webkit-text-size-adjust: 100%;
          -ms-text-size-adjust: 100%;
          color: #c7c8ca;
          font-size: 10px;
          line-height: 15px;
          padding: 5px;
        "
      >
        <tr>
          <td>
            <div style="margin-top: 20px">
              &copy; ${brandName} ${.now?string("yyyy")} | ${msg("allRightsReserved")}
            </div>
          </td>
        </tr>
        <#if privacyUrl?has_content || contactUrl?has_content>
        <tr>
          <td>
            <div>
              <#if privacyUrl?has_content>
              <a
                href="${privacyUrl}"
                style="
                  -webkit-text-size-adjust: 100%;
                  -ms-text-size-adjust: 100%;
                  font-weight: normal;
                  color: #c7c8ca;
                "
                >${msg("privacy")}</a
              >
              </#if>
              <#if privacyUrl?has_content && contactUrl?has_content>|</#if>
              <#if contactUrl?has_content>
              <a
                href="${contactUrl}"
                style="
                  -webkit-text-size-adjust: 100%;
                  -ms-text-size-adjust: 100%;
                  font-weight: normal;
                  color: #c7c8ca;
                "
                >${msg("contactUs")}</a
              >
              </#if>
            </div>
          </td>
        </tr>
        </#if>
      </tfoot>
    </table>
  </body>
</html>
</#macro>
