import React, { useEffect, useState } from "react";
import { OverlayTrigger, Tooltip } from 'react-bootstrap';
import { TbCircleLetterA, TbCircleLetterC, TbCircleLetterS } from "react-icons/tb";

export default function PetitionRow(props) {
    /* 
        props expects:
        - idx
        - petition
        - name
    */
   const { docket_info, docket_numbers } = props.petition;
   
   const [isChecked, setIsChecked] = useState(false);

    const StatusTooltip = ({ children, text}) => {
        return (
            <OverlayTrigger
                overlay={<Tooltip>{text}</Tooltip>}
            >
                <div>{children}</div>
            </OverlayTrigger>
        )
    }
    
    const alertIcons = () => {
        const icons = []

        if (props.petition.county && props.petition.county !== "Philadelphia") {
            icons.push(
                <StatusTooltip 
                    key={"county-alert"}
                    text="This record might include counties other than Philadelphia County."
                >
                    <TbCircleLetterC style={{ fontSize: "x-large", color: "red" }} />
                </StatusTooltip>
            )
        }

        if (props.petition.category === "Archived") {
            icons.push(
                <StatusTooltip 
                    key={"archive-alert"}
                    text="This record is archived"
                >
                    <TbCircleLetterA style={{ fontSize: "x-large", color: "orange" }} />
                </StatusTooltip>
            )
        } else if (props.petition.category !== "Docket") {
            icons.push(
                <StatusTooltip 
                    key={"summary-alert"}
                    text="This record is from a court summary"
                >
                    <TbCircleLetterS style={{ fontSize: "x-large", color: "blue" }} />
                </StatusTooltip>
            )
        }

        return icons
    }

    const petitionNums = () => {
        const nums = [];
        if (docket_info.otn) {
            nums.push(docket_info.otn);
        }
        for (const num of docket_numbers) {
            nums.push(num);
        };
        return nums
    }

    const omitColor = isChecked ? "lightgrey" : "";

    function handleCheckboxChange(e) {
        if (!isChecked) {
            props.setDoNotGenerate([
                ...props.doNotGenerate, 
                ...petitionNums()
            ]);
            props.setOmitCount(props.omitCount + 1);
        } else {
            const newOmissions = props.doNotGenerate.filter(num => !petitionNums().includes(num));
            props.setDoNotGenerate(newOmissions);
            props.setOmitCount(props.omitCount - 1);
        }
        setIsChecked(!isChecked);
    }

    useEffect(() => {
        const omitted = petitionNums().filter(num => props.doNotGenerate.includes(num));
        if (omitted.length > 0) {
            setIsChecked(true);
        }
        // eslint-disable-next-line
    }, [])

    return (
        <tr style={{color: omitColor}}>
            <td>{alertIcons()}</td>
            <td>{props.idx + 1}</td>
            <td>{docket_info.otn}</td>
            <td>
                <ul style={{ listStyleType: "none", margin: "0", padding: "0" }}>
                    {docket_numbers.map((num, i) => <li key={i}>{num}</li>)}
                </ul>
            </td>
            <td>
                Commonwealth of Pennsylvania v. {props.name}
            </td>
            <td>
                <input 
                    type="checkbox"
                    checked={isChecked}
                    style={{ accentColor: "grey" }}
                    onChange={handleCheckboxChange}
                />
            </td>
        </tr>
    )
}