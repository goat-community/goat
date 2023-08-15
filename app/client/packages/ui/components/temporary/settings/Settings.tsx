// import { useState } from "react";
//
// import { makeStyles } from "../../../lib/ThemeProvider";
// import { Divider } from "../../DataDisplay/Divider";
// import { Text } from "../../theme";
// import DashboardLayout from "../DashboardLayout";
// import Organization from "./organization/Organization";
// import PrivacyPreferences from "./privacyPreferences/PrivacyPreferences";
// import SubscriptionSettings from "./subscription/SubscriptionSettings";
//
// const Settings = () => {
//   const [currentSetting, setCurrentSetting] = useState<{ children: React.ReactNode; value: string }>({
//     children: <Organization />,
//     value: "Organization",
//   });
//
//   const { classes, cx } = useStyles();
//
//   return (
//     <DashboardLayout>
//       <div className={classes.wrapper}>
//         <div className={classes.sideBarSection}>
//           <span
//             onClick={() =>
//               setCurrentSetting({
//                 children: <Organization />,
//                 value: "Organization",
//               })
//             }>
//             <Text
//               typo="body 2"
//               className={
//                 currentSetting.value === "Organization" ? classes.selectedSidebarText : classes.SidebarText
//               }>
//               Organization
//             </Text>
//           </span>
//           <Divider width="100%" color="main" className={classes.hr} />
//           <span
//             onClick={() =>
//               setCurrentSetting({
//                 children: <SubscriptionSettings />,
//                 value: "Subscription",
//               })
//             }>
//             <Text
//               typo="body 2"
//               className={
//                 currentSetting.value === "Subscription" ? classes.selectedSidebarText : classes.SidebarText
//               }>
//               Subscription
//             </Text>
//           </span>
//           <Divider width="100%" color="main" className={classes.hr} />
//           <span
//             onClick={() =>
//               setCurrentSetting({
//                 children: <PrivacyPreferences />,
//                 value: "Privacy preferences",
//               })
//             }>
//             <Text
//               typo="body 2"
//               className={
//                 currentSetting.value === "Privacy preferences"
//                   ? classes.selectedSidebarText
//                   : classes.SidebarText
//               }>
//               Privacy preferences
//             </Text>
//           </span>
//           <Divider width="100%" color="main" className={classes.hr} />
//         </div>
//         <div className={classes.mainSection}>{currentSetting.children}</div>
//       </div>
//     </DashboardLayout>
//   );
// };
//
// const useStyles = makeStyles({ name: { Settings } })((theme) => ({
//   wrapper: {
//     display: "flex",
//     gap: theme.spacing(4),
//   },
//   SidebarText: {
//     // padding: theme.spacing(1) theme.spacing(4),
//     padding: `${theme.spacing(1)}px ${theme.spacing(4)}px`,
//     cursor: "pointer",
//     "&:hover": {
//       backgroundColor: theme.colors.palette[theme.isDarkModeEnabled ? "dark" : "light"].greyVariant2 + "50",
//     },
//   },
//   selectedSidebarText: {
//     padding: `${theme.spacing(1)}px ${theme.spacing(4)}px`,
//     cursor: "pointer",
//     backgroundColor: theme.colors.palette.focus.main + "14",
//   },
//   hr: {
//     margin: `${theme.spacing(1)}px 0`,
//   },
//   mainSection: {
//     flexGrow: "1",
//   },
//   sideBarSection: {
//     minWidth: "268px",
//     "@media (max-width: 1268px)": {
//       minWidth: "168px",
//     },
//   },
// }));
//
// export default Settings;
