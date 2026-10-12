<#import "template.ftl" as layout>
<@layout.emailLayout artwork="verify_email.png">
    <tr>
      <td>
        <div style="${properties.titleStyle}">
          <h2>${msg("eventUpdatePasswordTitle")}</h2>
        </div>
      </td>
    </tr>
    <tr>
      <td>
        <div
          style="${properties.infoContentStyle}"
        >
          ${kcSanitize(msg("eventUpdatePasswordBodyHtml",event.date,event.ipAddress))?no_esc}
        </div>
      </td>
    </tr>
</@layout.emailLayout>