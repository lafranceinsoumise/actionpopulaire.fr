import PropTypes from "prop-types";
import React, { useState } from "react";
import useSWR from "swr";

import { Banner, BackButton } from "./StyledComponents";
import ConfirmContact from "./ConfirmContact";
import ContactForm from "./ContactForm";
import ContactSuccess from "./ContactSuccess";

import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";

const CreateContactPage = (props) => {
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState(null);
  const [data, setData] = useState(null);
  const [step, setStep] = useState(0);

  const { data: session } = useSWR("/api/session/");
  const { data: userGroups } = useSWR("/api/groupes/");

  const user = session ? session?.user : undefined;
  const groups = userGroups ? userGroups?.groups : undefined;
  const pageIsReady =
    typeof user !== "undefined" && typeof groups !== "undefined";

  const submitForm = (data) => {
    setData(data);
    setStep(1);
  };

  const confirmData = () => {
    setStep(2);
  };

  const goBack = () => {
    setStep((step) => Math.max(0, step - 1));
  };

  const resetForm = () => {
    setData(null);
    setStep(0);
  };

  return (
    <div>
      <Banner />
      <main style={{ margin: "0 auto", maxWidth: 680, padding: "1.5rem" }}>
        <PageFadeIn
          ready={pageIsReady}
          wait={
            <>
              <Skeleton
                boxes={1}
                style={{ height: 56, marginBottom: "1.5rem" }}
              />
              <Skeleton />
            </>
          }
        >
          {step === 0 && (
            <>
              <BackButton link route="events">
                Retour à l'accueil
              </BackButton>
              <ContactForm
                onSubmit={submitForm}
                initialData={data}
                groups={groups}
                errors={errors}
                isLoading={isLoading}
              />
            </>
          )}
          {step === 1 && (
            <>
              <BackButton onClick={goBack} />
              <ConfirmContact
                isLoading={isLoading}
                data={data}
                onConfirm={confirmData}
                onBack={goBack}
              />
            </>
          )}
          {step === 2 && (
            <>
              <BackButton onClick={resetForm} />
              <ContactSuccess user={user} onReset={resetForm} />
            </>
          )}
        </PageFadeIn>
      </main>
    </div>
  );
};

export default CreateContactPage;
