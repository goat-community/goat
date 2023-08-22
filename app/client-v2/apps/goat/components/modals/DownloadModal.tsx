import { SelectField } from "@p4b/ui/components/Inputs";
import { Text, Button } from "@p4b/ui/components/theme";
import { makeStyles } from "@p4b/ui/lib/ThemeProvider";

interface DownloadModalProps {
  name: React.ReactNode;
  changeState: (value: { name: string; icon: React.ReactNode; value: string } | null) => void;
}

const DownloadModal = (props: DownloadModalProps) => {
  const { name, changeState } = props;

  const { classes } = useStyles();

  // Dumb Data
  // options to put in the select
  const staticData = [
    {
      name: "URL",
      value: "url",
    },
    {
      name: "Shapefile",
      value: "shapefile",
    },
    {
      name: "Geopackage",
      value: "geopackage",
    },
    {
      name: "Geobuf",
      value: "geobuf",
    },
    {
      name: "CSV",
      value: "csv",
    },
    {
      name: "XLSX",
      value: "xlsx",
    },
    {
      name: "KML",
      value: "kml",
    },
  ];

  return (
    <div>
      <Text typo="body 1" className={classes.bold}>
        {name ? name : ""}
      </Text>
      <SelectField
        className={classes.selectInput}
        options={staticData}
        size="small"
        label="Download Format"
      />
      <Text typo="label 1">
        Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean
        massa. Cum sociis natoque penatibus et magnis{" "}
      </Text>
      <div className={classes.buttons}>
        <Button variant="noBorder" onClick={() => changeState(null)}>
          CANCEL
        </Button>
        <Button variant="noBorder">DOWNLOAD</Button>
      </div>
    </div>
  );
};
const useStyles = makeStyles({ name: { DownloadModal } })((theme) => ({
  selectInput: {
    margin: `${theme.spacing(3)}px 0px`,
  },
  bold: {
    fontWeight: 800,
  },
  italic: {
    fontStyle: "italic",
  },
  buttons: {
    display: "flex",
    alignItems: "center",
    justifyContent: "end",
    gap: theme.spacing(2),
    marginTop: theme.spacing(3),
  },
}));
export default DownloadModal;
