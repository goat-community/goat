import { stackMiddlewares } from "@/middlewares/stackMiddlewares";
import { withAuth } from "@/middlewares/withAuth";
import { withCookies } from "@/middlewares/withCookies";
import { withLanguage } from "@/middlewares/withLanguage";
import { withOrganization } from "@/middlewares/withOrganization";

export default stackMiddlewares([withCookies, withLanguage, withAuth, withOrganization]);
