const htmlString = `<div id="popup" class="ol-popup" >
                <div class="header" id="popup-header" style="margin-top: 0px;font-size: larger;padding: 0px;/* float: right; */border-radius: 5px;width: 95%;/* border: 1px solid #2fac45; */padding-left: 5px;">
                    <span>Attributes</span>
                </div>
            <a href="#" id="popup-closer" class="ol-popup-closer" style="color:grey;"></a>
            <div id="popup-content" style="padding:10px;border:1px solid;border-color:lightgrey;border-radius: 5px;margin-top: 2px;margin-bottom: 5px;width: 100%;">
            <table>
            <tbody>
                <tr>
                    <td style="padding: 1px 1px"><label>Type: </label></td>
                    <td style="padding: 1px 1px">
                       <span class="right_side">
                        <select id="ways_type">
                          <option value="way">Way</option>    
                          <option value="bridge">Bridge</option>
                        </select>
                      </span>
                    </td>
                </tr>
            </tbody>
            </table>
            </div>
         <div style="text-align:center;display:inline-block;float: right;">            
            <button style="height: 30px; width: auto; border: 1px solid;background: none;box-shadow: none;border-radius: 0px;" class="popup-button"  id="btnNoFeature">Clear</button>            
            <button style="height: 30px; width: auto; color:#2fac45;background-color: none;border: 1px solid;background: none;box-shadow: none;border-radius: 0px;" class="popup-button"  id="btnYesFeature">Save</button>
        </div>
    </div>`;

export default htmlString;
