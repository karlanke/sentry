import React from 'react';

import {mount} from 'enzyme';
import OnboardingWelcome from 'app/views/onboarding/welcome';
import ConfigStore from 'app/stores/configStore';

describe('OnboardingWelcome', function() {
  it('renders', function() {
    const name = 'Rick Snachez';
    ConfigStore.loadInitialData({user: {name, options: {}}});

    const wrapper = mount(<OnboardingWelcome />, TestStubs.routerContext());

    expect(
      wrapper
        .find('p')
        .first()
        .text()
    ).toEqual(expect.stringContaining('Rick'));
  });

  it('calls onComplete when progressing', function() {
    const onComplete = jest.fn();
    const wrapper = mount(
      <OnboardingWelcome active onComplete={onComplete} />,
      TestStubs.routerContext()
    );

    wrapper
      .find('Button[priority="primary"]')
      .first()
      .simulate('click');

    expect(onComplete).toHaveBeenCalled();
  });

  it('disables the next step button when it is not active', function() {
    const onComplete = jest.fn();
    const wrapper = mount(
      <OnboardingWelcome onComplete={onComplete} />,
      TestStubs.routerContext()
    );

    wrapper
      .find('Button[priority="primary"]')
      .first()
      .simulate('click');

    expect(onComplete).not.toHaveBeenCalled();
  });
});
