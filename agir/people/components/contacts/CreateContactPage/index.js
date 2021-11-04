import React, { useCallback, useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import useSWR from "swr";

import { routeConfig } from "@agir/front/app/routes.config";
import { useDispatch } from "@agir/front/globalContext/GlobalContext";
import { setBackLink } from "@agir/front/globalContext/actions";
import { validateContact, createContact } from "./api";

import { Banner, BackButton, PageContent } from "./StyledComponents";
import ConfirmContact from "./ConfirmContact";
import ContactForm from "./ContactForm";
import ContactSuccess from "./ContactSuccess";

import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";

const STEPS = [null, "valider", "succes"];

const CreateContactPage = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const params = useParams();

  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState(null);
  const [data, setData] = useState({});
  const step = Math.max(STEPS.indexOf(params?.step), 0);

  const { data: session } = useSWR("/api/session/");
  const { data: userGroups } = useSWR("/api/groupes/");

  const user = session ? session?.user : undefined;
  const groups = userGroups ? userGroups?.groups : undefined;
  const pageIsReady =
    typeof user !== "undefined" && typeof groups !== "undefined";

  /**
   * Handles submission of the contact form (1st step) data for validation only
   * delegating the actual saving of the data to next step. Renders the 2nd step upon
   * success and display field errors upon failure.
   * @type {object}   The form field data object
   */
  const submitForm = useCallback(
    async (formData) => {
      setIsLoading(true);
      setErrors({});
      const result = await validateContact(formData);
      setIsLoading(false);
      if (result.errors || !result.valid) {
        setErrors(result.errors);
        return;
      }
      setData(formData);
      navigate(routeConfig.createContact.getLink({ step: STEPS[1] }));
    },
    [navigate]
  );

  /**
   * Handles submission of the contact form data for actually creating the
   * contact. Renders the 3rd step upon success and the 1st upon failure.
   */
  const confirmData = useCallback(async () => {
    setIsLoading(true);
    setErrors({});
    const result = await createContact(data);
    setIsLoading(false);
    if (result.errors) {
      setErrors(result.errors);
      navigate(routeConfig.createContact.getLink({ step: STEPS[0] }));
      return;
    }
    navigate(routeConfig.createContact.getLink({ step: STEPS[2] }), {
      replace: true,
    });
    // Reset everything, except the selected group
    setData((data) => ({
      group: data.group,
    }));
  }, [data, navigate]);

  const goToFirstStep = useCallback(() => {
    navigate(routeConfig.createContact.getLink({ step: STEPS[0] }));
  }, [navigate]);

  useEffect(() => {
    typeof window !== "undefined" && window.scrollTo({ top: 0 });
  }, [step]);

  useEffect(() => {
    step > 0
      ? dispatch(
          setBackLink({
            to: routeConfig.createContact.getLink({ step: STEPS[0] }),
          })
        )
      : null;
  }, [dispatch, step]);

  return (
    <div>
      <Banner />
      <PageContent>
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
              <BackButton disabled={isLoading} link route="events">
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
              <BackButton disabled={isLoading} onClick={goToFirstStep} />
              <ConfirmContact
                isLoading={isLoading}
                data={data}
                onConfirm={confirmData}
                onBack={goToFirstStep}
              />
            </>
          )}
          {step === 2 && (
            <>
              <BackButton onClick={goToFirstStep} />
              <ContactSuccess data={data} user={user} onReset={goToFirstStep} />
            </>
          )}
        </PageFadeIn>
      </PageContent>
    </div>
  );
};
export default CreateContactPage;
