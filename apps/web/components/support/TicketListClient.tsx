"use client";

import dynamic from "next/dynamic";

// Rendered in the browser only, like the other support pages, so the phone layout is right from
// the first frame (see useSupportMobile).
const TicketList = dynamic(() => import("@/components/support/TicketList"), { ssr: false });

const TicketListClient = () => <TicketList />;

export default TicketListClient;
