<#import "template.ftl" as layout>
<@layout.emailLayout artwork="verify_email.png">
    <tr>
      <td>
        <div style="${properties.titleStyle}">
          <h2>${msg("eventRemoveTotpTitle")}</h2>
        </div>
      </td>
    </tr>
    <tr>
      <td>
        <div
          style="${properties.infoContentStyle}"
        >
          ${kcSanitize(msg("eventRemoveTotpBodyHtml",event.date,event.ipAddress))?no_esc}
        </div>
      </td>
    </tr>
</@layout.emailLayout>