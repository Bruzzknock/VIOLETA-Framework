import type {ReactNode} from 'react';
import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

type FeatureItem = {
  title: string;
  Svg: React.ComponentType<React.ComponentProps<'svg'>>;
  description: ReactNode;
};

const FeatureList: FeatureItem[] = [
  {
    title: 'Triadic Integration',
    Svg: require('@site/static/img/undraw_connected-world_anke.svg').default,
    description: (
      <>
        VIOLETA systematically aligns <strong>skills</strong>, <strong>emotions</strong>, and <strong>game mechanics</strong>,
        ensuring that every game interaction supports meaningful real-world learning.
      </>
    ),
  },
  {
    title: 'Adaptive Challenge',
    Svg: require('@site/static/img/undraw_progress-overview_wl8n.svg').default,
    description: (
      <>
        Using <strong>STACK</strong>, the framework dynamically adjusts cognitive load and difficulty,
        so learners stay engaged and feel progressively more competent as they play.
      </>
    ),
  },
  {
    title: 'Flexible & Creative',
    Svg: require('@site/static/img/undraw_processing-thoughts_wakg.svg').default,
    description: (
      <>
        VIOLETA balances structure with creative freedom. Designers can craft unique themes and mechanics
        while following clear steps that guide skill mapping and emotional design.
      </>
    ),
  },
];

function Feature({title, Svg, description}: FeatureItem) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        <Svg className={styles.featureSvg} role="img" />
      </div>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures(): ReactNode {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
