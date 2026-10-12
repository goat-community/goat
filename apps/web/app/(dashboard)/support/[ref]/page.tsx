"use client";

import { use } from "react";

import TicketViewClient from "@/components/support/TicketViewClient";

// `params` is a Promise since Next 16 and is unwrapped with `use`, as the other dynamic routes here do.
const SupportTicketPage = (props: { params: Promise<{ ref: string }> }) => {
  const { ref } = use(props.params);
  return <TicketViewClient ticketRef={ref} />;
};

export default SupportTicketPage;
