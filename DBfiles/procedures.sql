DELIMITER //

CREATE PROCEDURE UpdateMemberStatus(member_id VARCHAR(15))
BEGIN
    DECLARE active_subscriptions INT;

    -- Count the number of active subscriptions for the member
    SELECT COUNT(*) INTO active_subscriptions
    FROM SUBSCRIPTION S
    JOIN PLANS P ON S.PLAN_ID = P.PLAN_ID
    WHERE S.MEM_ID = member_id
      AND DATE_ADD(S.START_DATE, INTERVAL P.DURATION DAY) >= CURDATE();

    -- Update the member's status based on their subscription status
    IF active_subscriptions > 0 THEN
        UPDATE MEMBERS SET STATUS = 'Active' WHERE MEM_ID = member_id;
    ELSE
        UPDATE MEMBERS SET STATUS = 'Inactive' WHERE MEM_ID = member_id;
    END IF;
END //

DELIMITER ;

DELIMITER //

CREATE TRIGGER AfterInsertSubscription
AFTER INSERT ON SUBSCRIPTION
FOR EACH ROW
BEGIN
    CALL UpdateMemberStatus(NEW.MEM_ID);
END //

DELIMITER ;

DELIMITER //

CREATE TRIGGER AfterDeleteSubscription
AFTER DELETE ON SUBSCRIPTION
FOR EACH ROW
BEGIN
    CALL UpdateMemberStatus(OLD.MEM_ID);
END //

DELIMITER ;

DELIMITER //

CREATE TRIGGER AfterUpdateSubscription
AFTER UPDATE ON SUBSCRIPTION
FOR EACH ROW
BEGIN
    IF OLD.START_DATE <> NEW.START_DATE THEN
        CALL UpdateMemberStatus(NEW.MEM_ID);
    END IF;
END //

DELIMITER ;

