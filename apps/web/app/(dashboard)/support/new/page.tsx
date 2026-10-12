import { Suspense } from "react";

import NewTicketFormClient from "@/components/support/NewTicketFormClient";

// useSearchParams needs a Suspense boundary under the app router.
const NewSupportTicketPage = () => (
  <Suspense>
    <NewTicketFormClient />
  </Suspense>
);

export default NewSupportTicketPage;
