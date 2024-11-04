import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import "@mui/material";
import type { CardProps } from "@mui/material";
import {
  Button,
  Card,
  CardContent,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  Stack,
  Typography,
} from "@mui/material";
import { styled } from "@mui/material/styles";
import React from "react";

export type PlanCardData = {
  title: string;
  description: string;
  buttonText: string;
  highlights: string[];
  active?: boolean;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  featuresHeader?: any;
  featuresSubHeader?: string; // e.g Everything in Starter, plus:
  trialDaysLabel?: string | React.ReactNode;
};

interface CustomCardProps extends CardProps {
  active?: boolean;
}

const StyledCard = styled(({ active: _active, ...other }: CustomCardProps) => (
  <Card {...other} />
))<CustomCardProps>(({ theme, active = false }) => ({
  maxWidth: "345px",
  padding: theme.spacing(2),
  textAlign: "center",
  boxShadow: theme.shadows[0],
  border: active ? `2px solid ${theme.palette.primary.main}` : `1px solid ${theme.palette.divider}`,
  display: "flex",
  flexDirection: "column",
  justifyContent: "space-between",
}));

const StyledDivider = styled(Divider)(({ theme }) => ({
  marginTop: theme.spacing(3),
  marginBottom: theme.spacing(2),
}));

export function PlanCard({ plan }: { plan: PlanCardData }) {
  return (
    <StyledCard active={plan.active}>
      <CardContent
        sx={{ flex: 1, display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
        <Stack spacing={4}>
          <Stack>
            <Typography variant="h6" fontWeight="bold">
              {plan.title}
            </Typography>
            {plan.trialDaysLabel && (
              <Typography variant="body2" color="text.secondary">
                {plan.trialDaysLabel}
              </Typography>
            )}
          </Stack>
          <Typography variant="body2">{plan.description}</Typography>
        </Stack>
        <Button variant="contained" color="primary" fullWidth disabled={plan.active} sx={{ mt: 4 }}>
          {plan.buttonText}
        </Button>
      </CardContent>
      <StyledDivider />
      <CardContent sx={{ px: 0 }}>
        <Typography variant="body1" fontWeight="bold">
          {plan.featuresHeader || "What's included"}
        </Typography>
        {plan.featuresSubHeader && (
          <Typography variant="body2" fontWeight="bold" color="text.secondary">
            {plan.featuresSubHeader}
          </Typography>
        )}
        <List>
          {plan.highlights.map((feature) => (
            <ListItem key={feature}>
              <ListItemIcon sx={{ minWidth: (theme) => theme.spacing(8) }}>
                <CheckCircleIcon color="primary" />
              </ListItemIcon>
              <Typography variant="body2">{feature}</Typography>
            </ListItem>
          ))}
        </List>
      </CardContent>
    </StyledCard>
  );
}

export default PlanCard;
