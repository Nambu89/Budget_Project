import CountUp from '../reactbits/CountUp';

interface Props {
  value: number;
  prefix?: string;
  suffix?: string;
  decimals?: number;
  className?: string;
}

export default function AnimatedNumber({
  value,
  prefix = '',
  suffix = ' \u20AC',
  decimals = 2,
  className = '',
}: Props) {
  return (
    <CountUp
      to={value}
      prefix={prefix}
      suffix={suffix}
      decimals={decimals}
      separator="."
      className={className}
      duration={1200}
    />
  );
}
