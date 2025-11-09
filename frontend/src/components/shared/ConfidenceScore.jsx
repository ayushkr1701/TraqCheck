import Badge from './Badge';

export default function ConfidenceScore({ confidence }) {
  if (confidence === null || confidence === undefined) {
    return <Badge variant="default">N/A</Badge>;
  }

  const percentage = Math.round(confidence * 100);

  let variant = 'error';
  if (percentage >= 90) variant = 'success';
  else if (percentage >= 70) variant = 'info';
  else if (percentage >= 50) variant = 'warning';

  return (
    <Badge variant={variant}>
      {percentage}% confidence
    </Badge>
  );
}
