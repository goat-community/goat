import io
import json
import os
import shutil
import time
from typing import Any

import geojson
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from starlette.responses import JSONResponse

from app.schemas.scenario import ScenarioBase, ScenarioImport


class CRUDScenario:
    def import_scenario(self, db: Session, *, obj_in: ScenarioImport) -> JSONResponse:
        obj_in_data = jsonable_encoder(obj_in)
        obj_in_data["payload"] = json.dumps(obj_in_data["payload"], separators=(",", ":"))
        sql = text(
            """SELECT import_changeset_scenario(:scenario_id,:user_id,jsonb_build_object(:layer_name,CAST(:payload as jsonb)))"""
        )
        result = db.execute(sql, obj_in_data).fetchone()
        return JSONResponse(content=result[0])

    def export_scenario(self, db: Session, *, obj_in: ScenarioBase) -> Any:
        obj_in_data = jsonable_encoder(obj_in)
        sql = text("""SELECT * FROM export_changeset_scenario(:scenario_id)""")
        result = db.execute(sql, obj_in_data).fetchone()
        dicts = dict(result[0])
        dir_path = "/tmp/exports/{}/".format(time.strftime("%Y%m%d-%H%M%S"))
        os.makedirs(dir_path)
        for key in dicts.keys():
            with open(dir_path + "/{}.geojson".format(key), "w") as f:
                geojson.dump(dicts[key], f)
        file_name = "scenario_export_{}".format(time.strftime("%Y%m%d-%H%M%S"))
        shutil.make_archive(file_name, "zip", dir_path)
        with open(file_name + ".zip", "rb") as f:
            data = f.read()
        os.remove(file_name + ".zip")
        shutil.rmtree(dir_path[0 : len(dir_path) - 1])
        response = StreamingResponse(io.BytesIO(data), media_type="application/zip")
        response.headers["Content-Disposition"] = "attachment; filename={}.zip".format(file_name)

        return response

    def upload_scenario(self, db: Session, *, obj_in: ScenarioBase) -> Any:
        obj_in_data = jsonable_encoder(obj_in)
        sql = text(
            """SELECT * FROM network_modification(:scenario_id);SELECT * FROM population_modification(:scenario_id);"""
        )
        db.execute(sql, obj_in_data)
        return {"msg": "Scenarios are reflected."}

    def delete_scenario(self, db: Session, *, obj_in: ScenarioBase) -> Any:
        obj_in_data = jsonable_encoder(obj_in)
        sql = text(
            """DELETE FROM scenarios WHERE scenario_id=:scenario_id;SELECT network_modification(:scenario_id);"""
        )
        db.execute(sql, obj_in_data)
        return {"msg": "All changes are reverted."}


scenario = CRUDScenario()
